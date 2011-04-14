# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2011 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
Loading and defaults for the different textformats used for Syntax Highlighting.
"""

from __future__ import unicode_literals

from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QApplication, QColor, QFont, QPalette, QTextCharFormat, QTextFormat

import app


# When textFormatData() is requested for the first time, it is loaded from the config
# When the settings are changed, it is cleared again so that it is reloaded when
# requested again.


def formatData(type):
    """Returns a TextFormatData instance of type 'editor' or 'printer'."""
    if _currentData[type] is None:
        _currentData[type] = TextFormatData(QSettings().value('{0}_scheme'.format(type), 'default'))
    return _currentData[type]

def _resetFormatData():
    global _currentData
    _currentData = {
        'editor': None,
        'printer': None,
    }

app.settingsChanged.connect(_resetFormatData, -100) # before all others
_resetFormatData()

    
class TextFormatData(object):
    """Encapsulates all settings in the Fonts & Colors page for a scheme."""
    def __init__(self, scheme):
        """Loads the data from scheme."""
        self.font = None
        self.baseColors = {}
        self.defaultStyles = {}
        self.allStyles = {}
        self.load(scheme)
        
    def load(self, scheme):
        s = QSettings()
        s.beginGroup("fontscolors/" + scheme)
        
        # load font
        self.font = QFont(s.value("fontfamily", "monospace"))
        self.font.setPointSizeF(float(s.value("fontsize", 10.0)))
        
        # load base colors
        s.beginGroup("basecolors")
        for name in baseColors:
            if s.contains(name):
                self.baseColors[name] = QColor(s.value(name))
            else:
                self.baseColors[name] = baseColorDefaults[name]()
        s.endGroup()
        
        # load default styles
        s.beginGroup("defaultstyles")
        for name in defaultStyles:
            self.defaultStyles[name] = f = QTextCharFormat(defaultStyleDefaults[name])
            s.beginGroup(name)
            loadTextFormat(f, s)
            s.endGroup()
        s.endGroup()
        
        # load specific styles
        s.beginGroup("allstyles")
        for group, styles in allStyles:
            self.allStyles[group]= {}
            s.beginGroup(group)
            for name in styles:
                default = allStyleDefaults[group].get(name)
                self.allStyles[group][name] = f = QTextCharFormat(default) if default else QTextCharFormat()
                s.beginGroup(name)
                loadTextFormat(f, s)
                s.endGroup()
            s.endGroup()
        s.endGroup()
        
    def save(self, scheme):
        s = QSettings()
        s.beginGroup("fontscolors/" + scheme)
        
        # save font
        s.setValue("fontfamily", self.font.family())
        s.setValue("fontsize", self.font.pointSizeF())
        
        # save base colors
        for name in baseColors:
            s.setValue("basecolors/"+name, self.baseColors[name].name())
        
        # save default styles
        s.beginGroup("defaultstyles")
        for name in defaultStyles:
            s.beginGroup(name)
            saveTextFormat(self.defaultStyles[name], s)
            s.endGroup()
        s.endGroup()
        
        # save all specific styles
        s.beginGroup("allstyles")
        for group, styles in allStyles:
            s.beginGroup(group)
            for name in styles:
                s.beginGroup(name)
                saveTextFormat(self.allStyles[group][name], s)
                s.endGroup()
            s.endGroup()
        s.endGroup()

    def textFormat(self, group, name):
        inherit = inherits[group].get(name)
        f = QTextCharFormat(self.defaultStyles[inherit]) if inherit else QTextCharFormat()
        f.merge(self.allStyles[group][name])
        return f
    
    def palette(self):
        """Returns a basic palette with text, background, selection and selection background filled in."""
        p = QApplication.palette()
        p.setColor(QPalette.Text, self.baseColors['text'])
        p.setColor(QPalette.Base, self.baseColors['background'])
        p.setColor(QPalette.HighlightedText, self.baseColors['selectiontext'])
        p.setColor(QPalette.Highlight, self.baseColors['selectionbackground'])
        return p
        

def saveTextFormat(fmt, settings):
    if fmt.hasProperty(QTextFormat.FontWeight):
        settings.setValue('bold', fmt.fontWeight() >= 70)
    else:
        settings.remove('bold')
    if fmt.hasProperty(QTextFormat.FontItalic):
        settings.setValue('italic', fmt.fontItalic())
    else:
        settings.remove('italic')
    if fmt.hasProperty(QTextFormat.TextUnderlineStyle):
        settings.setValue('underline', fmt.fontUnderline())
    else:
        settings.remove('underline')
    if fmt.hasProperty(QTextFormat.ForegroundBrush):
        settings.setValue('textColor', fmt.foreground().color().name())
    else:
        settings.remove('textColor')
    if fmt.hasProperty(QTextFormat.BackgroundBrush):
        settings.setValue('backgroundColor', fmt.background().color().name())
    else:
        settings.remove('backgroundColor')
    if fmt.hasProperty(QTextFormat.TextUnderlineColor):
        settings.setValue('underlineColor', fmt.underlineColor().name())
    else:
        settings.remove('underlineColor')
    
def loadTextFormat(fmt, settings):
    if settings.contains('bold'):
        fmt.setFontWeight(QFont.Bold if settings.value('bold') in (True, 'true') else QFont.Normal)
    if settings.contains('italic'):
        fmt.setFontItalic(settings.value('italic') in (True, 'true'))
    if settings.contains('underline'):
        fmt.setFontUnderline(settings.value('underline') in (True, 'true'))
    if settings.contains('textColor'):
        fmt.setForeground(QColor(settings.value('textColor')))
    if settings.contains('backgroundColor'):
        fmt.setBackground(QColor(settings.value('backgroundColor')))
    if settings.contains('underlineColor'):
        fmt.setUnderlineColor(QColor(settings.value('underlineColor')))



baseColors = (
    'text',
    'background',
    'selectiontext',
    'selectionbackground',
    'current',
    'mark',
    'error',
    'search',
    'match',
    'paper',
    'musichighlight',
)

baseColorDefaults = dict(
    text =                lambda: QApplication.palette().color(QPalette.Text),
    background =          lambda: QApplication.palette().color(QPalette.Base),
    selectiontext =       lambda: QApplication.palette().color(QPalette.HighlightedText),
    selectionbackground = lambda: QApplication.palette().color(QPalette.Highlight),
    current =             lambda: QColor(255, 252, 149),
    mark =                lambda: QColor(192, 192, 255),
    error =               lambda: QColor(255, 192, 192),
    search =              lambda: QColor(192, 255, 192),
    match =               lambda: QColor(0, 192, 255),
    paper =               lambda: QColor(242, 224, 168),
    musichighlight =      lambda: QApplication.palette().color(QPalette.Highlight),
)

defaultStyles = (
    'keyword',
    'function',
    'variable',
    'value',
    'string',
    'escape',
    'comment',
    'error',
)


def _defaultStyleDefaults():
    keyword = QTextCharFormat()
    keyword.setFontWeight(QFont.Bold)
    
    function = QTextCharFormat(keyword)
    function.setForeground(QColor(0, 0, 192))
    
    variable = QTextCharFormat()
    variable.setForeground(QColor(0, 0, 255))
    
    value = QTextCharFormat()
    value.setForeground(QColor(128, 128, 0))
    
    string = QTextCharFormat()
    string.setForeground(QColor(192, 0, 0))
    
    escape = QTextCharFormat()
    escape.setForeground(QColor(0, 128, 128))
    
    comment = QTextCharFormat()
    comment.setForeground(QColor(128, 128, 128))
    comment.setFontItalic(True)
    
    error = QTextCharFormat()
    error.setForeground(QColor(255, 0, 0))
    error.setFontUnderline(True)
    
    return locals()
    
defaultStyleDefaults = _defaultStyleDefaults()
del _defaultStyleDefaults


def _allStyleDefaults():
    lilypond = {}
    lilypond['markup'] = f = QTextCharFormat()
    f.setForeground(QColor(0, 128, 0))
    lilypond['grob'] = f = QTextCharFormat()
    f.setForeground(QColor(192, 0, 192))
    lilypond['context'] = f = QTextCharFormat(f)
    f.setFontWeight(QFont.Bold)
    
    html = {}
    
    scheme = {}
    scheme['scheme'] = f = QTextCharFormat()
    f.setForeground(QColor(160, 73, 0))
    scheme['lilypond'] = f = QTextCharFormat(f)
    f.setFontWeight(QFont.Bold)
    
    latex = {}
    docbook = {}
    texinfo = {}
    
    del f
    return locals()

allStyleDefaults = _allStyleDefaults()
del _allStyleDefaults



allStyles = (
    ('lilypond', (
        'pitch',
        'duration',
        'slur',
        'dynamic',
        'articulation',
        'chord',
        'beam',
        'check',
        'repeat',
        'keyword',
        'command',
        'specifier',
        'usercommand',
        'markup',
        'lyricmode',
        'lyrictext',
        'delimiter',
        'context',
        'grob',
        'property',
        'variable',
        'uservariable',
        'value',
        'string',
        'stringescape',
        'comment',
        'error',
        )),
    ('html', (
        'tag',
        'lilypondtag',
        'attribute',
        'value',
        'entityref',
        'string',
        'comment',
        )),
    ('scheme', (
        'scheme',
        'number',
        'lilypond',
        'string',
        'comment',
        )),
    ('texinfo', (
        'keyword',
        'block',
        'attribute',
        'escapechar',
        'verbatim',
        'comment',
    ))
)


inherits = {
    'lilypond': {
        'keyword': 'keyword',
        'command': 'function',
        'markup': 'function',
        'repeat': 'function',
        'specifier': 'variable',
        'usercommand': 'variable',
        'delimiter': 'keyword',
        'property': 'variable',
        'variable': 'variable',
        'value': 'value',
        'string': 'string',
        'stringescape': 'escape',
        'comment': 'comment',
        'error': 'error',
    },
    'html': {
        'tag': 'keyword',
        'lilypondtag': 'function',
        'attribute': 'variable',
        'value': 'value',
        'entityref': 'escape',
        'string': 'string',
        'comment': 'comment',
    },
    'scheme': {
        'number': 'value',
        'string': 'string',
        'comment': 'comment',
    },
    'texinfo': {
        'keyword': 'keyword',
        'block': 'function',
        'attribute': 'variable',
        'escapechar': 'escape',
        'verbatim': 'string',
        'comment': 'comment',
    }
        
}


        
