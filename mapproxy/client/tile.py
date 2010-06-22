# This file is part of the MapProxy project.
# Copyright (C) 2010 Omniscale <http://omniscale.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mapproxy.client.http import retrieve_image

class TMSClient(object):
    def __init__(self, url, format='png'):
        self.url = url
        self.format = format
    
    def get_tile(self, tile_coord):
        x, y, z = tile_coord
        url = '%s/%d/%d/%d.%s' % (self.url, z, x, y, self.format)
        return retrieve_image(url)
    
    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.url, self.format)

class TileClient(object):
    def __init__(self, url_template):
        self.url_template = url_template
        self.url = url_template.template + url_template.format
    def get_tile(self, tile_coord):
        url = self.url_template.substitute(tile_coord)
        return retrieve_image(url)
    
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.url_template)

class TileURLTemplate(object):
    """
    >>> t = TileURLTemplate('http://foo/tiles/%(z)s/%(x)d/%(y)s.png')
    >>> t.substitute((7, 4, 3))
    'http://foo/tiles/3/7/4.png'

    >>> t = TileURLTemplate('http://foo/tiles/%(z)s/%(x)d/%(y)s.png')
    >>> t.substitute((7, 4, 3))
    'http://foo/tiles/3/7/4.png'

    >>> t = TileURLTemplate('http://foo/tiles/%(tc_path)s.png')
    >>> t.substitute((7, 4, 3))
    'http://foo/tiles/03/000/000/007/000/000/004.png'
    """
    def __init__(self, template, format='png'):
        self.template= template
        self.format = format
        self.with_quadkey = True if '%(quadkey)' in template else False
        self.with_tc_path = True if '%(tc_path)' in template else False
    
    def substitute(self, tile_coord):
        x, y, z = tile_coord
        data = dict(x=x, y=y, z=z, format=self.format)
        if self.with_quadkey:
            data['quadkey'] = quadkey(tile_coord)
        if self.with_tc_path:
            data['tc_path'] = tilecache_path(tile_coord)
        return self.template % data
    
    def __repr__(self):
        return '%s(%r, format=%r)' % (
            self.__class__.__name__, self.template, self.format)

def tilecache_path(tile_coord):
    """
    >>> tilecache_path((1234567, 87654321, 9))
    '09/001/234/567/087/654/321'
    """
    x, y, z = tile_coord
    parts = ("%02d" % z,
             "%03d" % int(x / 1000000),
             "%03d" % (int(x / 1000) % 1000),
             "%03d" % (int(x) % 1000),
             "%03d" % int(y / 1000000),
             "%03d" % (int(y / 1000) % 1000),
             "%03d" % (int(y) % 1000))
    return '/'.join(parts)

def quadkey(tile_coord):
    """
    >>> quadkey((0, 0, 1))
    '0'
    >>> quadkey((1, 0, 1))
    '1'
    >>> quadkey((1, 2, 2))
    '21'
    """
    x, y, z = tile_coord
    quadKey = ""
    for i in range(z,0,-1):
        digit = 0
        mask = 1 << (i-1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadKey += str(digit)
    return quadKey
