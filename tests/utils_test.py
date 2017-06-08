import sys, os
sys.path.insert(0, os.path.abspath('..'))
import unittest
import urllib2


# Ignore Warning
import logging
logger = logging.getLogger()
logger.setLevel(40)

from src import utils

class UtilsTestCase(unittest.TestCase):

    def test_fetch_vimeo_thumb(self):
        video1 = 'https://vimeo.com/68856967'
        req = urllib2.Request('http://www.google.fr')
        try:
            urllib2.urlopen(req)
            self.assertTrue('http://i.vimeocdn.com/video/441364174_640.jpg' in utils.fetch_vimeo_thumb(video1))
        except IOError, e:
            print "Connect Error:", e.reason[1]
            self.assertTrue('https://i.vimeocdn.com/video/536038298_640.jpg' in utils.fetch_vimeo_thumb(video1))

    def test_get_embed_code_for_url(self):
        video1 = 'https://vimeo.com/123456789'
        (hst1, ec1) = utils.get_embed_code_for_url(video1)
        self.assertTrue('vimeo.com' in hst1)
        self.assertTrue('<iframe src="https://player.vimeo.com/video/123456789" width="500" '+
'height="281" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>' in ec1)
        video2 = 'https://www.canal-u.tv/123456789'
        (hst2, ec2) = utils.get_embed_code_for_url(video2)
        self.assertTrue('www.canal-u.tv' in hst2)
        self.assertTrue('<iframe src="https://www.canal-u.tv/embed.1/123456789?width=100%&amp;height=100%&amp" width="550" '+
'height="306" frameborder="0" allowfullscreen scrolling="no"></iframe>' in ec2)
        video3 = 'https://youtube.com/123456789'
        (hst3, ec3) = utils.get_embed_code_for_url(video3)
        self.assertTrue('youtube.com' in hst3)
        self.assertTrue('<p>Unsupported video provider ({0})</p>'.format(hst3) in ec3)

    def test_get_video_src(video_link):
        

# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
