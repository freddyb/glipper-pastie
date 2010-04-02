# Glipper - Clipboardmanager for GNOME
# Copyright (C) 2007 Glipper Team
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#

#XXX ripped together from original nopaste.py, snippets.py and http://pastie.org/459763
#XXX by Frederik B

import urllib, os, os.path, webbrowser, threading
#import httplib, urllib, os, os.path, webbrowser, threading
import glipper

from gettext import gettext as _

def info():
   info = {"Name": _("Pastie"), 
      "Description": _("Make use of the Pastie Nopaste-Service"),
      "Preferences": True}
   return info


languageList = ['Bash (shell)', 'C/C++', 'CSS', 'HTML (ERB / Rails)',
    'HTML / XML', 'Java', 'Javascript', 'PHP', 'Perl', 'Plain text', 'Python',
    'Ruby', 'Ruby on Rails', 'SQL', 'YAML']
languageDict= {'Objective-C/C++':'objective-c++', 'ActionScript':'actionscript',
    'Ruby':'ruby', 'Ruby on Rails':'ruby_on_rails', 'Diff':'diff',
    'Plain text':'plain_text', 'C/C++':'c++', 'CSS':'css', 'Java':'java',
    'Javascript':'javascript', 'HTML / XML':'html',
    'HTML (ERB / Rails)':'html_rails', 'Bash (shell)':'shell-unix-generic',
    'SQL':'sql', 'PHP':'php', 'Python':'python', 'Pascal':'pascal', 'Perl':'perl',
    'YAML':'yaml', 'C#':'csharp', 'Go':'go', 'Apache (config)':'apache',
    'Lua':'lua', 'Io':'io', 'Lisp (common)':'lisp', 'D':'d', 'Erlang':'erlang',
    'Fortran':'fortran', 'Haskell':'haskell',
    'Literate Haskell':'literate_haskell', 'Makefile':'makefile',
   'Scala':'scala', 'Scheme':'scheme', 'Smarty':'smarty', 'INI':'ini',
    'Nu':'nu', 'TeX':'tex', 'Clojure':'clojure'} 

class Pastie(threading.Thread):
   def __init__(self, lang, nick, desc, text):
      threading.Thread.__init__(self)
      global languageDict
      if lang in languageDict:
         self.lang = languageDict[lang]
      elif lang in languageDict.values():    
         self.lang = lang
      else:
         self.lang = 'plain_text'
      self.nick = desc
      self.desc = desc	      
      self.text = text

   def run(self):
      form = {
         "paste[display_name]": self.nick,
			"paste[parser]": self.lang,  #'plain_text',
			"paste[body]": self.text,
			"paste[authorization]": 'burger',
			"paste[restricted]": '1' # marked as private.
		}
      f = urllib.urlopen("http://pastie.org/pastes", urllib.urlencode(form))
      f.close()
      url = f.geturl()
      webbrowser.open(url)




def on_activate(menuitem, lang):
   cf = confFile("r")
   pastie = Pastie(lang, cf.getNick(), _("pasted by Glipper"), glipper.get_history_item(0))
   cf.close()
   pastie.start()


def init():
   item = gtk.MenuItem(_("Pastie"))
   glipper.add_menu_item(item)
   menu = gtk.Menu()
   global languageList   
   for lang in languageList:
      subitem = gtk.MenuItem(glipper.format_item(lang))
      subitem.connect('activate', on_activate, lang)
      menu.append(subitem)
   
   menu.show_all()
   item.set_submenu(menu)


def on_show_preferences(parent):
   preferences(parent).show()


#config file class:
class confFile:
   def __init__(self, mode):
      self.mode = mode

      dir = os.environ["HOME"] + "/.glipper/plugins"
      if (mode == "r") and (not os.path.exists(dir + "/pastie.conf")):
         self.lang = 13
         self.nick = _("Glipper user")
         return
      if not os.path.exists(dir):
         os.makedirs(dir)
      self.file = open(dir + "/pastie.conf", mode)

      if mode == "r":
         self.lang = int(self.file.readline()[:-1])
         self.nick = self.file.readline()[:-1]

   def setLang(self, lang):
      self.lang = lang
   def getLang(self):
      return self.lang
   def setNick(self, nick):
      self.nick = nick
   def getNick(self):
      return self.nick
   def close(self):
      if not 'file' in dir(self):
         return
      try:
         if self.mode == "w":
            self.file.write(str(self.lang) + "\n")
            self.file.write(self.nick + "\n")
      finally:
         self.file.close()

#preferences dialog:
import gtk
import gtk.glade

class preferences:
   def __init__(self, parent):
      gladeFile = gtk.glade.XML(os.path.dirname(__file__) + "/nopaste.glade")
      self.prefWind = gladeFile.get_widget("preferences")
      self.prefWind.set_transient_for(parent)
      self.nickEntry = gladeFile.get_widget("nickEntry")
      self.langBox = gladeFile.get_widget("langBox")
      self.prefWind.connect('response', self.on_prefWind_response)

      #read configurations
      f = confFile("r")
      self.nickEntry.set_text(f.getNick())
      self.langBox.set_active(f.getLang())
      f.close()

   def destroy(self, window):
      window.destroy()

   def show(self):
      self.prefWind.show_all()

   #EVENTS:
   def on_prefWind_response(self, widget, response):
      if response == gtk.RESPONSE_DELETE_EVENT or response == gtk.RESPONSE_CLOSE:
         f = confFile("w")
         f.setNick(self.nickEntry.get_text())
         f.setLang(self.langBox.get_active())
         f.close()
         widget.destroy()   
      
