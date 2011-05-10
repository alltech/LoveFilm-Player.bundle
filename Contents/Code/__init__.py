####################################################################################################

VIDEO_PREFIX = "/video/blinkbox"

NAME = L('Title')

ART = 'art-default.jpg'
ICON = 'icon-default.png'
TV_SHOWS = 'icon-tvshows.png'
FILMS = 'icon-films.png'

MOVIES_FREE = 'http://www.blinkbox.com/Movies/Free'
TV_FREE = 'http://www.blinkbox.com/TV/Free'

####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
    
    # Initialize the plugin
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, Locale.LocalString('Title'), ICON, ART)
    Plugin.AddViewGroup("Basic", viewMode = "InfoList", mediaType = "items")
    Plugin.AddViewGroup("Basic", viewMode = "List", mediaType = "items")
    
    # Setup the artwork associated with the plugin
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

# This main function will setup the displayed items. This will depend if the user is currently
# logged in.
def MainMenu():
    dir = MediaContainer(disabledViewModes=["Coverflow"], title1 = Locale.LocalString('Title'))
    
    # Movies
    dir.Append(Function(
        DirectoryItem(
            MovieMenu,
            Locale.LocalString('Movies'),
            thumb = R(FILMS))))
    
    # TV Shows
    dir.Append(Function(
        DirectoryItem(
            TVMenu,
            Locale.LocalString('TVShows'),
            thumb = R(TV_SHOWS))))
    
    return dir

####################################################################################################
# Movies
####################################################################################################

# This is the main function for displaying all available free movies. 
def MovieMenu(sender, current_page = 0):
    dir = MediaContainer(disabledViewModes=["Coverflow"], title1=Locale.LocalString('Movies'))

    if current_page != 0:
        dir.replaceParent = True
    
    # Request the appropriate page
    free_movies_url = MOVIES_FREE + '?page=' + str(current_page + 1)
    movies = HTTP.Request(free_movies_url)
    movies_free = HTML.ElementFromString(movies)
    
    movie_assets = movies_free.xpath("//div[@class='movieAsset']")
    for movie_asset in movie_assets:
		
        # Parse the movie details to determine all associated content.
        title_details = parseMovieTitle(movie_asset)
        
        dir.Append(WebVideoItem(
            title_details['url'],
            title = title_details['name'],
            subtitle = title_details['subtitle'],
            summary = title_details['description'],
            thumb = title_details['image']))
    
    next_page = movies_free.xpath("//a[@class='pag_forw bundle']")
    if len(next_page) > 0:
        dir.Append(Function(
            DirectoryItem(
                MovieMenu,
                "Next"),
            current_page = current_page + 1))
    
    return dir

# This function will parse a specific 'movieAsset' to determine the associated information about
# the title.
def parseMovieTitle(item):
    summary_node = item.xpath(".//div[@class='summary']/a")[0]
    
    # Attempt to locate the title's name.
    name = ''
    try:
        name = summary_node.xpath(".//span/text()")[0]
        name = name.lstrip().rstrip()
    except:
        pass
    
    # Attempt to locate the url to the title.
    url = ''
    try:
        url = summary_node.get('href')
    except:
        pass
    
    # Attempt to locate the associated image.
    image = ''
    try:
        image = item.xpath(".//img")[0].get('src')
    except:
        pass
	
    subtitle = ''
    try:
        subtitle = item.xpath(".//div[@class='message']/p/span/text()")[0]
    except:
        pass
    
    description = ''
    try:
        description = item.xpath(".//span[@class='msg']/text()")[0]
    except:
        pass
    
    parsed = {}
    parsed['name'] = name
    parsed['url'] = url
    parsed['image'] = image
    parsed['subtitle'] = subtitle
    parsed['description'] = description
    
    return parsed

####################################################################################################
# TV Shows
####################################################################################################

# This function displays the top level menu for all availabe TV shows. When selected, it will then
# display the available series.
def TVMenu(sender, current_page = 0):
    dir = MediaContainer(disabledViewModes = ["Coverflow"], title1 = Locale.LocalString('TVShows'))

    if current_page != 0:
        dir.replaceParent = True
    
    # Request the appropriate page
    free_tv_shows_url = TV_FREE + '?page=' + str(current_page + 1)
    tv_shows = HTTP.Request(free_tv_shows_url)
    tv_shows_free = HTML.ElementFromString(tv_shows)
    
    movie_assets = tv_shows_free.xpath("//div[@class='movieAsset']")
    for movie_asset in movie_assets:
		
        title_details = parseTvTitle(movie_asset)
        
        dir.Append(Function(
            DirectoryItem(
                TVSeriesMenu,
                title_details['name'],
                subtitle = title_details['subtitle'],
                summary = title_details['description'],
                thumb = title_details['image']),
            name = title_details['name'],
            url = title_details['url']))

    next_page = tv_shows_free.xpath("//a[@class='pag_forw bundle']")
    if len(next_page) > 0:
        dir.Append(Function(
            DirectoryItem(
                TVMenu,
                "Next"),
            current_page = current_page + 1))
    
    return dir

# This function will parse a specific 'movieAsset' to determine the associated information about
# the title.
def parseTvTitle(item):
    summary_node = item.xpath(".//div[@class='summary']/a")[0]
    
    # Attempt to locate the title's name.
    name = ''
    try:
        name = summary_node.xpath(".//span/text()")[0]
    except:
        pass
    
    # Attempt to locate the url to the title.
    url = ''
    try:
        url = summary_node.get('href')
    except:
        pass
    
    # Attempt to locate the associated image.
    image = ''
    try:
        image = item.xpath(".//img")[0].get('src')
    except:
        pass
	
    subtitle = ''
    try:
        subtitle = item.xpath(".//div[@class='message']/p/text()")[0]
    except:
        pass
    
    description = ''
    try:
        description = item.xpath(".//span[@class='msg']/text()")[0]
    except:
        pass
    
    parsed = {}
    parsed['name'] = name
    parsed['url'] = url
    parsed['image'] = image
    parsed['subtitle'] = subtitle
    parsed['description'] = description
    
    return parsed

# This function displays the individual series available for a specified tv show.
def TVSeriesMenu(sender, name = '', url = ''):
    dir = MediaContainer(disabledViewModes = ["Coverflow"], title1 = sender.title1, title2 = name)

    tv_series_string = HTTP.Request(url)
    tv_series = HTML.ElementFromString(tv_series_string)

    assets = tv_series.xpath("//div[@class='assetDetailed c']")
    for asset in assets:
		
        title_details = parseTvEpisodeTitle(asset)
        
        dir.Append(WebVideoItem(
            title_details['url'],
            title = title_details['name'],
            subtitle = title_details['subtitle'],
            summary = title_details['description'],
            thumb = title_details['image']))
    
    return dir

# This function will parse a specific 'assetDetailed c' to determine the associated information about
# the title.
def parseTvEpisodeTitle(item):
    
    # Attempt to locate the title's name.
    name = ''
    try:
        name = item.xpath(".//p[@class='title']/a/text()")[0]
    except:
        pass
    
    # Attempt to locate the url to the title.
    url = ''
    try:
        node = item.xpath(".//p[@class='title']/a")[0]
        url = node.get('href')
    except:
        pass
    
    # Attempt to locate the associated image.
    image = ''
    try:
        image = item.xpath(".//img")[0].get('src')
    except:
        pass
	
    subtitle = ''
    try:
        subtitle = item.xpath(".//p[@class='header']/text()")[0]
    except:
        pass
    
    description = ''
    try:
        description = item.xpath(".//p[@class='info']/text()")[0]
    except:
        pass
    
    parsed = {}
    parsed['name'] = name
    parsed['url'] = url
    parsed['image'] = image
    parsed['subtitle'] = subtitle
    parsed['description'] = description
    
    return parsed