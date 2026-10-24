from src.modules.local.main import LocalModule
from src.modules.web.main import WebModule
from src.modules.youtube.main import YouTubeModule


CORE_MODULES = {
    'local': LocalModule,
    'web': WebModule,
    'youtube': YouTubeModule
}
