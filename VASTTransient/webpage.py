# ztwang201605@gmail.com

from astropy.coordinates import SkyCoord

import os
import json
import pkg_resources

from .download import query_simbad, get_simbad_url

def _table_to_html(table):
    '''
    Function to convert astropy.Table to html

    Params:
    ----------
    table: astropy.Table
    '''
    table.convert_bytestring_to_unicode()
    df = table.to_pandas()
    return df.to_html()

class WebCreator:
    '''
    Class for creating simple webpage
    '''
    def __init__(self, htmlname, htmlpath='/import/ada1/zwan4817/', url='http://ada.physics.usyd.edu.au', port=8020, portbase='/import/ada1/zwan4817/'):
        '''
        Initiate TransientWeb Object

        Params:
        ----------
        htmlname: str
            filename for this html file
        url: str, ada url by default
            base url for your http server
        port: int, 8020 by default
            port used for setting up http server
        portbase: str, my ada1 folder by default
            base directory for setting up the port
        htmlpath: str
            path for saving html file
        '''
        self.url = url
        self.port = port
        self.portbase = portbase
        self.htmlpath = htmlpath
        self.htmlname = htmlname

        ###
        self.htmlcontent = ''

    def _gethref(self, href):
        '''
        Get correct href for the `a` tag

        Params:
        ----------
        href: str
            relative or absolute path for the link
        
        Returns:
        href_: str
        '''
        if len(href) == 0:
            return href
        if href[0] == '#': # avoid anchor
            return href
        if len(href) > 4:
            if href[:4] == 'http':
                return href
        return os.path.relpath(href, self.htmlpath)

    def _parsetagattr(self, tagattr=None):
        '''
        Parse tagattr into a string

        Params:
        ----------
        tagattr: Dict or NoneType
            Dict contains attribute for the tag
        
        Returns:
        ----------
        attrstr: str
        '''
        if tagattr is None: # if no tagattr, return an empty string
            return ''
        attrstr = ''
        for attr in tagattr:
            if attr.lower() == 'href' or attr.lower() == 'src':
                attrstr += ' {}="{}"'.format(attr, self._gethref(tagattr[attr]))
            else:
                attrstr += ' {}="{}"'.format(attr, tagattr[attr])
        return attrstr  

    def _createtag(self, tagname, tagattr=None, tagcontent=''):
        '''
        create html tag for further usage

        <tagname [tagattr]> tagcontent </tagname>

        Params:
        ---------
        tagname: str
        tagattr: Dict or NoneType
        tagcontent: str 

        See explaination above

        Returns:
        ----------
        htmltag: str
        '''
        htmltag = ''
        attrstr = self._parsetagattr(tagattr)
        htmltag += '\n<{}{}>\n'.format(tagname, attrstr)
        if tagname == 'hr': # no closing tag is allowed for hr
            return htmltag
        htmltag += tagcontent.strip('\n')
        htmltag += '\n</{}>\n'.format(tagname)
        return htmltag

    def addcontent(self, content):
        '''
        add content to self.htmlcontent

        Params:
        ----------
        content: str
            Any content to be added in the html
        '''
        self.htmlcontent += content

    def addtag(self, tagname, tagattr=None, tagcontent=''):
        '''
        add html tag to self.htmlcontent, you can use _createtag function to make a nested tag

        <tagname [tagattr]> tagcontent </tagname>

        Params:
        ---------
        tagname: str
        tagattr: Dict or NoneType
        tagcontent: str 

        See explaination above
        '''
        self.addcontent(self._createtag(tagname, tagattr, tagcontent))

    def savehtml(self, printinfo=False):
        with open(os.path.join(self.htmlpath, self.htmlname), 'w') as fp:
            fp.write(self.htmlcontent)
        if printinfo:
            htmlrelpath = os.path.relpath(os.path.join(self.htmlpath, self.htmlname), self.portbase)
            print(f'{self.url}:{self.port}/{htmlrelpath}')

class PipelineWeb:
    '''
    class for creating Transient webpage based on pipeline output
    '''
    def __init__(self, coord, htmlname, sourcepath):
        '''
        Params:
        ----------
        coord: tuple, list or SkyCoord
        '''
        ### coordinate
        if isinstance(coord, SkyCoord):
            self.ra = coord.ra.value
            self.dec = coord.dec.value
        if isinstance(coord, list) or isinstance(coord, tuple):
            self.ra, self.dec = coord
        self.sourcepath = sourcepath
        self.imagepath = os.path.join(self.sourcepath, 'img/')

        self.webcreator = WebCreator(
            htmlname, htmlpath = sourcepath
        )

    def addtitle(self):
        self.webcreator.addtag('h3', tagcontent='{}, {}'.format(self.ra, self.dec))
        self.webcreator.addtag('hr')

    def addarchival(self):
        ### add radio archival
        imagetag = self.webcreator._createtag(
            'img',
            {
                'src':os.path.join(self.imagepath, 'archival_lightcurve.png'),
                'height':250
            },
        )
        self.webcreator.addtag(
            'a',
            {'href':os.path.join(self.imagepath, 'archival_lightcurve.png')},
            imagetag
        )
        ### add wise-cc plot
        imagetag = self.webcreator._createtag(
            'img',
            {
                'src':os.path.join(self.imagepath, 'wise-cc.png'),
                'height':250
            },
        )
        self.webcreator.addtag(
            'a',
            {'href':os.path.join(self.imagepath, 'wise-cc.png')},
            imagetag
        )

        self.webcreator.addtag('hr')

    def addVASTlightcurve(self):
        ### add radio archival
        imagetag = self.webcreator._createtag(
            'img',
            {
                'src':os.path.join(self.imagepath, 'VASTlightcurve.png'),
                'height':250
            },
        )
        self.webcreator.addtag(
            'a',
            {'href':os.path.join(self.imagepath, 'VASTlightcurve.png')},
            imagetag
        )

        self.webcreator.addtag('hr')

    def addVASTcutout(self):
        ### add VAST StokesI
        imagepath = os.path.join(self.imagepath, 'StokesI_300.jpg')
        if os.path.exists(imagepath):
            self.webcreator.addtag('h5',tagcontent='VAST StokesI(300)')
            imagetag = self.webcreator._createtag(
                'img',
                {'src': imagepath, 'width':800},
            )
            self.webcreator.addtag(
                'a',
                {'href':imagepath},
                imagetag
            )
        ### add VAST StokesV
        imagepath = os.path.join(self.imagepath, 'StokesV_300.jpg')
        if os.path.exists(imagepath):
            self.webcreator.addtag('h5',tagcontent='VAST StokesV(300)')
            imagetag = self.webcreator._createtag(
                'img',
                {'src': imagepath, 'width':800},
            )
            self.webcreator.addtag(
                'a',
                {'href':imagepath},
                imagetag
            )

        self.webcreator.addtag('hr')

    def addSimbad(self):
        ### add link to simbad
        self.webcreator.addtag(
            'a',
            {'href': get_simbad_url((self.ra, self.dec), 60.)},
            'SIMBAD'
        )
        ### add simbad table
        simbadquery = query_simbad((self.ra, self.dec), 60.)
        if simbadquery is None:
            self.webcreator.addtag('p', tagcontent='No simbad objects within 60 arcsecs\n ')
        else:
            self.webcreator.addcontent(
                _table_to_html(simbadquery)
            )

        self.webcreator.addtag('hr')

    def addMultiWavelengthOverlay(self, ncols=4):
        # load setup files
        archivalradius_path = pkg_resources.resource_filename(
            __name__, './setups/multiwavelength_information.json'
        )
        with open(archivalradius_path) as fp:
            archivalradius = json.load(fp)

        # create a table
        self.webcreator.addtag('h5', tagcontent='Other Wavelength')
        figurecount = 0
        headerline = ''; imageline = ''
        tablehtml = '<table border="1">\n'
        for survey in archivalradius:
            radius = archivalradius[survey][0]
            survey = survey.replace(' ', '_')
            headerline += f'<td>{survey}</td>\n'
            # use function to add image
            pngpath = os.path.join(self.imagepath, f'{survey}_{radius}.png')
            imagetag = self.webcreator._createtag(
                'img',
                {'src': pngpath, 'width': 200, 'alt':f'{survey}-NO IMAGE'},
            )
            atag = self.webcreator._createtag(
                'a',
                {'href': pngpath},
                imagetag
            )
            imageline += f'<td>{atag}</td>\n'
            figurecount += 1

            # add linebreaker
            if figurecount == ncols:
                tablehtml += f'<tr>{headerline}</tr>\n<tr>{imageline}</tr>\n'
                figurecount = 0; headerline = ''; imageline = ''
        tablehtml += f'<tr>{headerline}</tr>\n<tr>{imageline}</tr>\n</table>'

        self.webcreator.addcontent(tablehtml)
        self.webcreator.addtag('hr')

    def addVASTrefcutout(self):
        ### add VAST StokesI - scale
        imagepath = os.path.join(self.imagepath, 'StokesI_300_scale.jpg')
        if os.path.exists(imagepath):
            self.webcreator.addtag('h5',tagcontent='VAST StokesI(300) - scale')
            imagetag = self.webcreator._createtag(
                'img',
                {'src': imagepath, 'width':800},
            )
            self.webcreator.addtag(
                'a',
                {'href':imagepath},
                imagetag
            )
        ### add VAST StokesI 600
        imagepath = os.path.join(self.imagepath, 'StokesI_600.jpg')
        if os.path.exists(imagepath):
            self.webcreator.addtag('h5',tagcontent='VAST StokesI(600)')
            imagetag = self.webcreator._createtag(
                'img',
                {'src': imagepath, 'width':800},
            )
            self.webcreator.addtag(
                'a',
                {'href':imagepath},
                imagetag
            )

        self.webcreator.addtag('hr')

    def makefullweb(self):
        self.addtitle()
        self.addVASTlightcurve()
        self.addarchival()
        self.addSimbad()
        self.addVASTcutout()
        self.addMultiWavelengthOverlay(ncols=5)
        self.addVASTrefcutout()

        self.webcreator.savehtml()


    

    




    