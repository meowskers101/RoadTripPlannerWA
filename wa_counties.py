# wa_counties.py
# Data file for Washington State counties, highways, and coordinates

import math
import os
import requests
import time

# Washington State Highway Connections Dictionary
wa_highway_connections = {
    "Adams": {
        "major_cities": ["Ritzville", "Othello"],
        "connections": {
            "Ritzville": {
                "I-90": ["Spokane (Spokane Co.)", "Moses Lake (Grant Co.)"],
                "US-395": ["Spokane (Spokane Co.)"]
            },
            "Othello": {
                "SR-26": ["Colfax (Whitman Co.)", "Vantage (Kittitas Co.)"],
                "SR-17": ["Moses Lake (Grant Co.)"]
            }
        }
    },
    
    "Asotin": {
        "major_cities": ["Clarkston", "Asotin"],
        "connections": {
            "Clarkston": {
                "US-12": ["Pomeroy (Garfield Co.)", "Lewiston ID"],
                "SR-129": ["Pomeroy (Garfield Co.)"]
            }
        }
    },
    
    "Benton": {
        "major_cities": ["Kennewick", "Richland", "Prosser"],
        "connections": {
            "Kennewick": {
                "I-82": ["Yakima (Yakima Co.)", "Umatilla OR"],
                "US-395": ["Pasco (Franklin Co.)"],
                "SR-240": ["Richland (Benton Co.)"]
            },
            "Prosser": {
                "I-82": ["Yakima (Yakima Co.)"],
                "SR-221": ["Paterson (Benton Co.)"]
            }
        }
    },
    
    "Chelan": {
        "major_cities": ["Wenatchee", "Leavenworth", "Chelan"],
        "connections": {
            "Wenatchee": {
                "US-2": ["Everett (Snohomish Co.)", "Spokane (Spokane Co.)"],
                "US-97": ["Okanogan (Okanogan Co.)", "Yakima (Yakima Co.)"],
                "SR-28": ["Quincy (Grant Co.)"]
            },
            "Leavenworth": {
                "US-2": ["Stevens Pass to Snohomish Co.", "Wenatchee (Chelan Co.)"]
            }
        }
    },
    
    "Clallam": {
        "major_cities": ["Port Angeles", "Sequim", "Forks"],
        "connections": {
            "Port Angeles": {
                "US-101": ["Sequim (Clallam Co.)", "Forks (Clallam Co.)"],
                "SR-112": ["Neah Bay (Clallam Co.)"]
            },
            "Sequim": {
                "US-101": ["Port Townsend (Jefferson Co.)"]
            }
        }
    },
    
    "Clark": {
        "major_cities": ["Vancouver", "Camas", "Battle Ground"],
        "connections": {
            "Vancouver": {
                "I-5": ["Portland OR", "Longview (Cowlitz Co.)"],
                "I-205": ["Portland OR"],
                "SR-14": ["Camas (Clark Co.)", "Stevenson (Skamania Co.)"]
            },
            "Camas": {
                "SR-14": ["Vancouver (Clark Co.)", "Stevenson (Skamania Co.)"]
            }
        }
    },
    
    "Columbia": {
        "major_cities": ["Dayton"],
        "connections": {
            "Dayton": {
                "US-12": ["Walla Walla (Walla Walla Co.)", "Pomeroy (Garfield Co.)"]
            }
        }
    },
    
    "Cowlitz": {
        "major_cities": ["Longview", "Kelso", "Castle Rock"],
        "connections": {
            "Longview": {
                "I-5": ["Vancouver (Clark Co.)", "Centralia (Lewis Co.)"],
                "SR-4": ["Cathlamet (Wahkiakum Co.)"],
                "SR-432": ["Longview (Cowlitz Co.)"]
            },
            "Castle Rock": {
                "I-5": ["Centralia (Lewis Co.)"],
                "SR-504": ["Mount St. Helens"]
            }
        }
    },
    
    "Douglas": {
        "major_cities": ["East Wenatchee", "Waterville"],
        "connections": {
            "East Wenatchee": {
                "US-2": ["Wenatchee (Chelan Co.)", "Spokane (Spokane Co.)"],
                "SR-28": ["Quincy (Grant Co.)"]
            },
            "Waterville": {
                "US-2": ["Coulee City (Grant Co.)"]
            }
        }
    },
    
    "Ferry": {
        "major_cities": ["Republic"],
        "connections": {
            "Republic": {
                "SR-20": ["Kettle Falls (Stevens Co.)", "Tonasket (Okanogan Co.)"],
                "SR-21": ["Curlew (Ferry Co.)"]
            }
        }
    },
    
    "Franklin": {
        "major_cities": ["Pasco", "Connell"],
        "connections": {
            "Pasco": {
                "I-182": ["Richland (Benton Co.)"],
                "US-395": ["Kennewick (Benton Co.)", "Ritzville (Adams Co.)"],
                "SR-124": ["Burbank (Walla Walla Co.)"]
            }
        }
    },
    
    "Garfield": {
        "major_cities": ["Pomeroy"],
        "connections": {
            "Pomeroy": {
                "US-12": ["Clarkston (Asotin Co.)", "Dayton (Columbia Co.)"],
                "SR-127": ["Dodge (Columbia Co.)"]
            }
        }
    },
    
    "Grant": {
        "major_cities": ["Moses Lake", "Ephrata", "Quincy"],
        "connections": {
            "Moses Lake": {
                "I-90": ["Spokane (Spokane Co.)", "Ellensburg (Kittitas Co.)"],
                "SR-17": ["Othello (Adams Co.)", "Coulee City (Grant Co.)"]
            },
            "Ephrata": {
                "US-2": ["Wenatchee (Chelan Co.)", "Spokane (Spokane Co.)"],
                "SR-28": ["East Wenatchee (Douglas Co.)"]
            }
        }
    },
    
    "Grays Harbor": {
        "major_cities": ["Aberdeen", "Hoquiam", "Montesano"],
        "connections": {
            "Aberdeen": {
                "US-101": ["Raymond (Pacific Co.)", "Port Angeles (Clallam Co.)"],
                "US-12": ["Olympia (Thurston Co.)"]
            },
            "Montesano": {
                "US-12": ["Olympia (Thurston Co.)"],
                "SR-8": ["Olympia (Thurston Co.)"]
            }
        }
    },
    
    "Island": {
        "major_cities": ["Oak Harbor", "Coupeville"],
        "connections": {
            "Oak Harbor": {
                "SR-20": ["Anacortes (Skagit Co.)", "Keystone Ferry"]
            },
            "Coupeville": {
                "SR-20": ["Port Townsend Ferry (Jefferson Co.)"]
            }
        }
    },
    
    "Jefferson": {
        "major_cities": ["Port Townsend", "Port Ludlow"],
        "connections": {
            "Port Townsend": {
                "SR-20": ["Keystone Ferry to Island Co."],
                "US-101": ["Sequim (Clallam Co.)", "Shelton (Mason Co.)"],
                "SR-19": ["Chimacum (Jefferson Co.)"]
            }
        }
    },
    
    "King": {
        "major_cities": ["Seattle", "Bellevue", "Renton", "Kent", "Auburn", "Federal Way"],
        "connections": {
            "Seattle": {
                "I-5": ["Everett (Snohomish Co.)", "Tacoma (Pierce Co.)"],
                "I-90": ["Bellevue (King Co.)", "Ellensburg (Kittitas Co.)"],
                "SR-99": ["Everett (Snohomish Co.)"],
                "SR-520": ["Bellevue (King Co.)"]
            },
            "Bellevue": {
                "I-405": ["Renton (King Co.)", "Bothell (Snohomish Co.)"],
                "I-90": ["Snoqualmie Pass to Kittitas Co."]
            }
        }
    },
    
    "Kitsap": {
        "major_cities": ["Bremerton", "Silverdale", "Port Orchard", "Poulsbo"],
        "connections": {
            "Bremerton": {
                "SR-3": ["Shelton (Mason Co.)", "Poulsbo (Kitsap Co.)"],
                "SR-16": ["Tacoma (Pierce Co.)"],
                "Seattle Ferry": ["Seattle (King Co.)"]
            },
            "Poulsbo": {
                "SR-305": ["Bainbridge Ferry to Seattle"]
            }
        }
    },
    
    "Kittitas": {
        "major_cities": ["Ellensburg", "Cle Elum"],
        "connections": {
            "Ellensburg": {
                "I-90": ["Seattle (King Co.)", "Moses Lake (Grant Co.)"],
                "I-82": ["Yakima (Yakima Co.)"],
                "US-97": ["Wenatchee (Chelan Co.)"]
            },
            "Cle Elum": {
                "I-90": ["Snoqualmie Pass to King Co."]
            }
        }
    },
    
    "Klickitat": {
        "major_cities": ["Goldendale", "White Salmon"],
        "connections": {
            "Goldendale": {
                "US-97": ["Yakima (Yakima Co.)", "The Dalles OR"]
            },
            "White Salmon": {
                "SR-14": ["Stevenson (Skamania Co.)", "Hood River OR"]
            }
        }
    },
    
    "Lewis": {
        "major_cities": ["Centralia", "Chehalis"],
        "connections": {
            "Centralia": {
                "I-5": ["Olympia (Thurston Co.)", "Longview (Cowlitz Co.)"],
                "US-12": ["Aberdeen (Grays Harbor Co.)", "Packwood (Lewis Co.)"]
            },
            "Chehalis": {
                "I-5": ["Olympia (Thurston Co.)", "Longview (Cowlitz Co.)"]
            }
        }
    },
    
    "Lincoln": {
        "major_cities": ["Davenport", "Sprague"],
        "connections": {
            "Davenport": {
                "US-2": ["Spokane (Spokane Co.)", "Coulee Dam (Grant Co.)"],
                "SR-25": ["Kettle Falls (Stevens Co.)"]
            },
            "Sprague": {
                "I-90": ["Spokane (Spokane Co.)", "Ritzville (Adams Co.)"]
            }
        }
    },
    
    "Mason": {
        "major_cities": ["Shelton"],
        "connections": {
            "Shelton": {
                "US-101": ["Olympia (Thurston Co.)", "Aberdeen (Grays Harbor Co.)"],
                "SR-3": ["Bremerton (Kitsap Co.)"]
            }
        }
    },
    
    "Okanogan": {
        "major_cities": ["Omak", "Okanogan", "Tonasket"],
        "connections": {
            "Omak": {
                "US-97": ["Wenatchee (Chelan Co.)", "Canadian Border"],
                "SR-20": ["Republic (Ferry Co.)"]
            },
            "Okanogan": {
                "US-97": ["Wenatchee (Chelan Co.)"],
                "SR-215": ["Nespelem (Okanogan Co.)"]
            }
        }
    },
    
    "Pacific": {
        "major_cities": ["Raymond", "South Bend"],
        "connections": {
            "Raymond": {
                "US-101": ["Aberdeen (Grays Harbor Co.)", "Astoria OR"],
                "SR-6": ["Chehalis (Lewis Co.)"]
            }
        }
    },
    
    "Pend Oreille": {
        "major_cities": ["Newport"],
        "connections": {
            "Newport": {
                "US-2": ["Spokane (Spokane Co.)", "Idaho"],
                "SR-20": ["Colville (Stevens Co.)"]
            }
        }
    },
    
    "Pierce": {
        "major_cities": ["Tacoma", "Lakewood", "Puyallup", "Gig Harbor"],
        "connections": {
            "Tacoma": {
                "I-5": ["Seattle (King Co.)", "Olympia (Thurston Co.)"],
                "SR-16": ["Bremerton (Kitsap Co.)", "Gig Harbor (Pierce Co.)"],
                "SR-7": ["Morton (Lewis Co.)"]
            },
            "Puyallup": {
                "SR-410": ["Mount Rainier", "Yakima (Yakima Co.)"]
            }
        }
    },
    
    "San Juan": {
        "major_cities": ["Friday Harbor"],
        "connections": {
            "Friday Harbor": {
                "Ferry": ["Anacortes (Skagit Co.)"]
            }
        }
    },
    
    "Skagit": {
        "major_cities": ["Mount Vernon", "Burlington", "Anacortes"],
        "connections": {
            "Mount Vernon": {
                "I-5": ["Bellingham (Whatcom Co.)", "Everett (Snohomish Co.)"],
                "SR-20": ["Anacortes (Skagit Co.)", "North Cascades"]
            },
            "Anacortes": {
                "SR-20": ["Mount Vernon (Skagit Co.)"],
                "Ferry": ["San Juan Islands"]
            }
        }
    },
    
    "Skamania": {
        "major_cities": ["Stevenson"],
        "connections": {
            "Stevenson": {
                "SR-14": ["Camas (Clark Co.)", "White Salmon (Klickitat Co.)"]
            }
        }
    },
    
    "Snohomish": {
        "major_cities": ["Everett", "Marysville", "Lynnwood", "Edmonds"],
        "connections": {
            "Everett": {
                "I-5": ["Bellingham (Whatcom Co.)", "Seattle (King Co.)"],
                "US-2": ["Stevens Pass to Chelan Co."],
                "SR-9": ["Arlington (Snohomish Co.)"]
            },
            "Marysville": {
                "I-5": ["Everett (Snohomish Co.)"],
                "SR-529": ["Everett (Snohomish Co.)"]
            }
        }
    },
    
    "Spokane": {
        "major_cities": ["Spokane", "Spokane Valley", "Cheney"],
        "connections": {
            "Spokane": {
                "I-90": ["Moses Lake (Grant Co.)", "Coeur d'Alene ID"],
                "US-2": ["Newport (Pend Oreille Co.)", "Davenport (Lincoln Co.)"],
                "US-395": ["Ritzville (Adams Co.)", "Colville (Stevens Co.)"]
            },
            "Cheney": {
                "I-90": ["Spokane (Spokane Co.)"]
            }
        }
    },
    
    "Stevens": {
        "major_cities": ["Colville", "Kettle Falls"],
        "connections": {
            "Colville": {
                "US-395": ["Spokane (Spokane Co.)", "Canadian Border"],
                "SR-20": ["Newport (Pend Oreille Co.)"]
            },
            "Kettle Falls": {
                "US-395": ["Colville (Stevens Co.)"],
                "SR-20": ["Republic (Ferry Co.)"]
            }
        }
    },
    
    "Thurston": {
        "major_cities": ["Olympia", "Lacey", "Tumwater"],
        "connections": {
            "Olympia": {
                "I-5": ["Tacoma (Pierce Co.)", "Centralia (Lewis Co.)"],
                "US-101": ["Shelton (Mason Co.)", "Aberdeen (Grays Harbor Co.)"],
                "SR-8": ["Aberdeen (Grays Harbor Co.)"]
            }
        }
    },
    
    "Wahkiakum": {
        "major_cities": ["Cathlamet"],
        "connections": {
            "Cathlamet": {
                "SR-4": ["Longview (Cowlitz Co.)", "Raymond (Pacific Co.)"]
            }
        }
    },
    
    "Walla Walla": {
        "major_cities": ["Walla Walla", "College Place"],
        "connections": {
            "Walla Walla": {
                "US-12": ["Dayton (Columbia Co.)", "Pasco (Franklin Co.)"],
                "US-730": ["Umatilla OR"]
            }
        }
    },
    
    "Whatcom": {
        "major_cities": ["Bellingham", "Blaine", "Ferndale"],
        "connections": {
            "Bellingham": {
                "I-5": ["Vancouver BC", "Mount Vernon (Skagit Co.)"],
                "SR-542": ["Mount Baker"],
                "SR-20": ["North Cascades"]
            },
            "Blaine": {
                "I-5": ["Canadian Border"]
            }
        }
    },
    
    "Whitman": {
        "major_cities": ["Pullman", "Colfax"],
        "connections": {
            "Pullman": {
                "US-195": ["Spokane (Spokane Co.)"],
                "SR-270": ["Moscow ID"]
            },
            "Colfax": {
                "US-195": ["Spokane (Spokane Co.)", "Pullman (Whitman Co.)"],
                "SR-26": ["Othello (Adams Co.)"]
            }
        }
    },
    
    "Yakima": {
        "major_cities": ["Yakima", "Sunnyside", "Toppenish"],
        "connections": {
            "Yakima": {
                "I-82": ["Ellensburg (Kittitas Co.)", "Kennewick (Benton Co.)"],
                "US-12": ["Packwood (Lewis Co.)", "Naches (Yakima Co.)"],
                "SR-410": ["Mount Rainier", "Puyallup (Pierce Co.)"],
                "US-97": ["Goldendale (Klickitat Co.)"]
            },
            "Sunnyside": {
                "I-82": ["Yakima (Yakima Co.)", "Prosser (Benton Co.)"]
            }
        }
    }
}

# Approximate coordinates (latitude, longitude) for each Washington county
# These are approximate county centroids
county_coords = {
    "Adams": (47.0, -118.5),
    "Asotin": (46.2, -117.2),
    "Benton": (46.25, -119.5),
    "Chelan": (47.9, -120.6),
    "Clallam": (48.1, -123.9),
    "Clark": (45.7, -122.5),
    "Columbia": (46.3, -117.9),
    "Cowlitz": (46.2, -122.7),
    "Douglas": (47.7, -119.7),
    "Ferry": (48.5, -118.5),
    "Franklin": (46.5, -118.9),
    "Garfield": (46.4, -117.6),
    "Grant": (47.2, -119.5),
    "Grays Harbor": (47.1, -123.8),
    "Island": (48.2, -122.6),
    "Jefferson": (47.8, -123.6),
    "King": (47.5, -121.8),
    "Kitsap": (47.6, -122.6),
    "Kittitas": (47.1, -120.5),
    "Klickitat": (45.9, -120.8),
    "Lewis": (46.6, -122.4),
    "Lincoln": (47.6, -118.4),
    "Mason": (47.3, -123.2),
    "Okanogan": (48.5, -119.8),
    "Pacific": (46.5, -123.8),
    "Pend Oreille": (48.6, -117.3),
    "Pierce": (47.0, -122.2),
    "San Juan": (48.5, -123.0),
    "Skagit": (48.5, -122.0),
    "Skamania": (45.9, -121.9),
    "Snohomish": (48.0, -121.7),
    "Spokane": (47.6, -117.4),
    "Stevens": (48.4, -117.8),
    "Thurston": (47.0, -122.9),
    "Wahkiakum": (46.3, -123.4),
    "Walla Walla": (46.1, -118.5),
    "Whatcom": (48.9, -122.0),
    "Whitman": (46.9, -117.5),
    "Yakima": (46.5, -120.7)
}

# City coordinates for major cities in Washington
city_coords = {
    # Adams County
    "Ritzville": (47.1274, -118.3797),
    "Othello": (46.8260, -119.1753),
    
    # Asotin County
    "Clarkston": (46.4163, -117.0421),
    "Asotin": (46.3396, -117.0488),
    
    # Benton County
    "Kennewick": (46.2112, -119.1372),
    "Richland": (46.2856, -119.2844),
    "Prosser": (46.2068, -119.7689),
    
    # Chelan County
    "Wenatchee": (47.4235, -120.3103),
    "Leavenworth": (47.5962, -120.6615),
    "Chelan": (47.8410, -120.0168),
    
    # Clallam County
    "Port Angeles": (48.1181, -123.4307),
    "Sequim": (48.0795, -123.1018),
    "Forks": (47.9501, -124.3854),
    
    # Clark County
    "Vancouver": (45.6387, -122.6615),
    "Camas": (45.5871, -122.3995),
    "Battle Ground": (45.7809, -122.5334),
    
    # Columbia County
    "Dayton": (46.3237, -117.9772),
    
    # Cowlitz County
    "Longview": (46.1382, -122.9382),
    "Kelso": (46.1468, -122.9085),
    "Castle Rock": (46.2751, -122.9076),
    
    # Douglas County
    "East Wenatchee": (47.4157, -120.2931),
    "Waterville": (47.6476, -119.6847),
    
    # Ferry County
    "Republic": (48.6482, -118.7375),
    
    # Franklin County
    "Pasco": (46.2396, -119.1006),
    "Connell": (46.6632, -118.8611),
    
    # Garfield County
    "Pomeroy": (46.4760, -117.6002),
    
    # Grant County
    "Moses Lake": (47.1301, -119.2781),
    "Ephrata": (47.3179, -119.5539),
    "Quincy": (47.2337, -119.8528),
    
    # Grays Harbor County
    "Aberdeen": (46.9754, -123.8157),
    "Hoquiam": (46.9809, -123.8894),
    "Montesano": (46.9812, -123.6026),
    
    # Island County
    "Oak Harbor": (48.2932, -122.6433),
    "Coupeville": (48.2193, -122.6863),
    
    # Jefferson County
    "Port Townsend": (48.1170, -122.7604),
    "Port Ludlow": (47.9257, -122.6826),
    
    # King County
    "Seattle": (47.6062, -122.3321),
    "Bellevue": (47.6101, -122.2015),
    "Renton": (47.4829, -122.2171),
    "Kent": (47.3809, -122.2348),
    "Auburn": (47.3073, -122.2285),
    "Federal Way": (47.3223, -122.3126),
    "Redmond": (47.6740, -122.1215),
    "Kirkland": (47.6815, -122.2087),
    "Sammamish": (47.6163, -122.0356),
    "Issaquah": (47.5301, -122.0326),
    
    # Kitsap County
    "Bremerton": (47.5673, -122.6326),
    "Silverdale": (47.6445, -122.6946),
    "Port Orchard": (47.5404, -122.6363),
    "Poulsbo": (47.7357, -122.6465),
    
    # Kittitas County
    "Ellensburg": (46.9965, -120.5478),
    "Cle Elum": (47.1954, -120.9395),
    
    # Klickitat County
    "Goldendale": (45.8204, -120.8217),
    "White Salmon": (45.7276, -121.4864),
    
    # Lewis County
    "Centralia": (46.7162, -122.9543),
    "Chehalis": (46.6620, -122.9640),
    
    # Lincoln County
    "Davenport": (47.6543, -118.1508),
    "Sprague": (47.2951, -117.9789),
    
    # Mason County
    "Shelton": (47.2151, -123.0999),
    
    # Okanogan County
    "Omak": (48.4110, -119.5275),
    "Okanogan": (48.3710, -119.5831),
    "Tonasket": (48.7096, -119.4378),
    
    # Pacific County
    "Raymond": (46.6865, -123.7326),
    "South Bend": (46.6631, -123.7957),
    
    # Pend Oreille County
    "Newport": (48.1782, -117.0443),
    
    # Pierce County
    "Tacoma": (47.2529, -122.4443),
    "Lakewood": (47.1717, -122.5185),
    "Puyallup": (47.1854, -122.2929),
    "Gig Harbor": (47.3295, -122.5801),
    
    # San Juan County
    "Friday Harbor": (48.5343, -123.0110),
    
    # Skagit County
    "Mount Vernon": (48.4212, -122.3340),
    "Burlington": (48.4757, -122.3255),
    "Anacortes": (48.5126, -122.6127),
    
    # Skamania County
    "Stevenson": (45.6876, -121.8845),
    
    # Snohomish County
    "Everett": (47.9790, -122.2021),
    "Marysville": (48.0518, -122.1771),
    "Lynnwood": (47.8209, -122.3151),
    "Edmonds": (47.8107, -122.3774),
    "Bothell": (47.7623, -122.2054),
    "Mukilteo": (47.9445, -122.3046),
    
    # Spokane County
    "Spokane": (47.6588, -117.4260),
    "Spokane Valley": (47.6732, -117.2394),
    "Cheney": (47.4874, -117.5758),
    
    # Stevens County
    "Colville": (48.5466, -117.9055),
    "Kettle Falls": (48.6115, -118.0555),
    
    # Thurston County
    "Olympia": (47.0379, -122.9007),
    "Lacey": (47.0343, -122.8232),
    "Tumwater": (47.0073, -122.9093),
    
    # Wahkiakum County
    "Cathlamet": (46.2043, -123.3832),
    
    # Walla Walla County
    "Walla Walla": (46.0646, -118.3430),
    "College Place": (46.0493, -118.3883),
    
    # Whatcom County
    "Bellingham": (48.7519, -122.4787),
    "Blaine": (48.9937, -122.7473),
    "Ferndale": (48.8465, -122.5910),
    
    # Whitman County
    "Pullman": (46.7312, -117.1796),
    "Colfax": (46.8801, -117.3644),
    
    # Yakima County
    "Yakima": (46.6021, -120.5059),
    "Sunnyside": (46.3232, -120.0087),
    "Toppenish": (46.3779, -120.3087),
}

# Map cities to their counties
city_to_county = {
    "Ritzville": "Adams", "Othello": "Adams",
    "Clarkston": "Asotin", "Asotin": "Asotin",
    "Kennewick": "Benton", "Richland": "Benton", "Prosser": "Benton",
    "Wenatchee": "Chelan", "Leavenworth": "Chelan", "Chelan": "Chelan",
    "Port Angeles": "Clallam", "Sequim": "Clallam", "Forks": "Clallam",
    "Vancouver": "Clark", "Camas": "Clark", "Battle Ground": "Clark",
    "Dayton": "Columbia",
    "Longview": "Cowlitz", "Kelso": "Cowlitz", "Castle Rock": "Cowlitz",
    "East Wenatchee": "Douglas", "Waterville": "Douglas",
    "Republic": "Ferry",
    "Pasco": "Franklin", "Connell": "Franklin",
    "Pomeroy": "Garfield",
    "Moses Lake": "Grant", "Ephrata": "Grant", "Quincy": "Grant",
    "Aberdeen": "Grays Harbor", "Hoquiam": "Grays Harbor", "Montesano": "Grays Harbor",
    "Oak Harbor": "Island", "Coupeville": "Island",
    "Port Townsend": "Jefferson", "Port Ludlow": "Jefferson",
    "Seattle": "King", "Bellevue": "King", "Renton": "King", "Kent": "King", 
    "Auburn": "King", "Federal Way": "King", "Redmond": "King", "Kirkland": "King",
    "Sammamish": "King", "Issaquah": "King",
    "Bremerton": "Kitsap", "Silverdale": "Kitsap", "Port Orchard": "Kitsap", "Poulsbo": "Kitsap",
    "Ellensburg": "Kittitas", "Cle Elum": "Kittitas",
    "Goldendale": "Klickitat", "White Salmon": "Klickitat",
    "Centralia": "Lewis", "Chehalis": "Lewis",
    "Davenport": "Lincoln", "Sprague": "Lincoln",
    "Shelton": "Mason",
    "Omak": "Okanogan", "Okanogan": "Okanogan", "Tonasket": "Okanogan",
    "Raymond": "Pacific", "South Bend": "Pacific",
    "Newport": "Pend Oreille",
    "Tacoma": "Pierce", "Lakewood": "Pierce", "Puyallup": "Pierce", "Gig Harbor": "Pierce",
    "Friday Harbor": "San Juan",
    "Mount Vernon": "Skagit", "Burlington": "Skagit", "Anacortes": "Skagit",
    "Stevenson": "Skamania",
    "Everett": "Snohomish", "Marysville": "Snohomish", "Lynnwood": "Snohomish", 
    "Edmonds": "Snohomish", "Bothell": "Snohomish", "Mukilteo": "Snohomish",
    "Spokane": "Spokane", "Spokane Valley": "Spokane", "Cheney": "Spokane",
    "Colville": "Stevens", "Kettle Falls": "Stevens",
    "Olympia": "Thurston", "Lacey": "Thurston", "Tumwater": "Thurston",
    "Cathlamet": "Wahkiakum",
    "Walla Walla": "Walla Walla", "College Place": "Walla Walla",
    "Bellingham": "Whatcom", "Blaine": "Whatcom", "Ferndale": "Whatcom",
    "Pullman": "Whitman", "Colfax": "Whitman",
    "Yakima": "Yakima", "Sunnyside": "Yakima", "Toppenish": "Yakima",
}

# Drive times between cities within the same county (computed in minutes from coordinates)
def _compute_intra_county_minutes():
    from itertools import combinations
    def haversine_km(a_lat, a_lon, b_lat, b_lon):
        R = 6371.0
        phi1 = math.radians(a_lat)
        phi2 = math.radians(b_lat)
        dphi = math.radians(b_lat - a_lat)
        dlambda = math.radians(b_lon - a_lon)
        x = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
        return 2 * R * math.asin(math.sqrt(x))

    counties = {}
    for city, county in city_to_county.items():
        counties.setdefault(county, []).append(city)

    result = {}
    for county, cities in counties.items():
        if len(cities) < 2:
            continue
        for a, b in combinations(cities, 2):
            if a in city_coords and b in city_coords:
                lat1, lon1 = city_coords[a]
                lat2, lon2 = city_coords[b]
                dist_km = haversine_km(lat1, lon1, lat2, lon2)
                # approximate driving distance and speed
                road_multiplier = 1.25
                road_km = dist_km * road_multiplier
                avg_speed_kmph = 50.0
                minutes = max(1, int(round((road_km / avg_speed_kmph) * 60.0)))
                result[(a, b)] = minutes
                result[(b, a)] = minutes
    return result

intra_county_drive_times = _compute_intra_county_minutes()


def get_city_drive_time(city1, city2):
    """Get drive time between two cities in seconds."""
    if city1 == city2:
        return 0
    
    # Check if cities are in same county
    different_counties = False
    if city1 in city_to_county and city2 in city_to_county:
        if city_to_county[city1] != city_to_county[city2]:
            different_counties = True

    # Allow using city-to-city estimates even across counties;
    # external APIs (if configured) will be preferred.
    google_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    ors_key = os.environ.get('ORS_API_KEY')
    
    # Try both orderings
    key1 = (city1, city2)
    key2 = (city2, city1)
    # If we have an explicit intra-county time, use it
    explicit = intra_county_drive_times.get(key1, intra_county_drive_times.get(key2, None))
    if explicit is not None:
        return int(explicit * 60)

    # Fall back to computing haversine distance between city coordinates if available
    if city1 in city_coords and city2 in city_coords:
        lat1, lon1 = city_coords[city1]
        lat2, lon2 = city_coords[city2]

        # Try external routing APIs if keys present
        google_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        ors_key = os.environ.get('ORS_API_KEY')
        if google_key:
            try:
                gm_seconds = _query_google_distance_matrix(lat1, lon1, lat2, lon2, google_key)
                if gm_seconds is not None:
                    return gm_seconds
            except Exception:
                pass

        if ors_key:
            try:
                ors_seconds = _query_ors_matrix(lat1, lon1, lat2, lon2, ors_key)
                if ors_seconds is not None:
                    return ors_seconds
            except Exception:
                pass

        # Haversine fallback with road-distance multiplier and realistic speeds
        def haversine_km(a_lat, a_lon, b_lat, b_lon):
            R = 6371.0
            phi1 = math.radians(a_lat)
            phi2 = math.radians(b_lat)
            dphi = math.radians(b_lat - a_lat)
            dlambda = math.radians(b_lon - a_lon)
            x = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
            return 2 * R * math.asin(math.sqrt(x))

        dist_km = haversine_km(lat1, lon1, lat2, lon2)
        # Choose multiplier/speed depending on whether cities are in different counties
        if different_counties:
            road_multiplier = 1.35
            avg_speed_kmph = 80.0
        else:
            road_multiplier = 1.25
            avg_speed_kmph = 50.0

        road_km = dist_km * road_multiplier
        hours = road_km / avg_speed_kmph
        seconds = int(max(30, round(hours * 3600)))
        return seconds

    # If we can't compute anything, return None
    return None


# --- External routing APIs (optional) ---
# If you set environment variable `GOOGLE_MAPS_API_KEY` or `ORS_API_KEY`,
# the code will attempt to query those services for more accurate driving times.

_dm_cache = {}

def _query_google_distance_matrix(lat1, lon1, lat2, lon2, api_key):
    """Query Google Maps Distance Matrix for driving duration (seconds)."""
    cache_key = ("gm", lat1, lon1, lat2, lon2)
    if cache_key in _dm_cache:
        return _dm_cache[cache_key]

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{lat1},{lon1}",
        "destinations": f"{lat2},{lon2}",
        "key": api_key,
        "mode": "driving",
        "departure_time": "now"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        elem = data.get('rows', [{}])[0].get('elements', [{}])[0]
        if elem.get('status') == 'OK':
            # Prefer duration in traffic when available (more Google-like)
            if 'duration_in_traffic' in elem and elem['duration_in_traffic']:
                seconds = int(elem['duration_in_traffic']['value'])
            elif 'duration' in elem and elem['duration']:
                seconds = int(elem['duration']['value'])
            else:
                seconds = None

            if seconds is not None:
                _dm_cache[cache_key] = seconds
                return seconds
    except Exception:
        pass
    return None


def _query_ors_matrix(lat1, lon1, lat2, lon2, api_key):
    """Query OpenRouteService matrix for driving duration (seconds)."""
    cache_key = ("ors", lat1, lon1, lat2, lon2)
    if cache_key in _dm_cache:
        return _dm_cache[cache_key]

    url = "https://api.openrouteservice.org/v2/matrix/driving-car"
    # ORS expects [lon, lat]
    body = {
        "locations": [[lon1, lat1], [lon2, lat2]],
        "metrics": ["duration"]
    }
    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    try:
        r = requests.post(url, json=body, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        # duration matrix [from][to] in seconds
        durations = data.get('durations')
        if durations and len(durations) > 0 and len(durations[0]) > 1:
            seconds = int(durations[0][1])
            _dm_cache[cache_key] = seconds
            return seconds
    except Exception:
        pass
    return None


def get_cities_by_county():
    """Organize cities by their county for dropdown display."""
    counties_dict = {}
    for city, county in city_to_county.items():
        if county not in counties_dict:
            counties_dict[county] = []
        counties_dict[county].append(city)
    
    # Sort cities within each county
    for county in counties_dict:
        counties_dict[county].sort()
    
    return counties_dict

# County adjacency graph - which counties border each other
# This is based on actual geographic boundaries
wa_county_graph = {
    "Adams": ["Franklin", "Grant", "Lincoln", "Whitman"],
    "Asotin": ["Garfield"],
    "Benton": ["Franklin", "Yakima", "Klickitat"],
    "Chelan": ["Douglas", "Kittitas", "Okanogan"],
    "Clallam": ["Jefferson"],
    "Clark": ["Cowlitz", "Skamania"],
    "Columbia": ["Garfield", "Walla Walla"],
    "Cowlitz": ["Clark", "Lewis", "Skamania", "Wahkiakum"],
    "Douglas": ["Chelan", "Grant", "Okanogan"],
    "Ferry": ["Lincoln", "Okanogan", "Pend Oreille", "Stevens"],
    "Franklin": ["Adams", "Benton", "Grant", "Walla Walla"],
    "Garfield": ["Asotin", "Columbia", "Whitman"],
    "Grant": ["Adams", "Douglas", "Franklin", "Kittitas", "Lincoln", "Okanogan"],
    "Grays Harbor": ["Jefferson", "Lewis", "Mason", "Pacific", "Thurston"],
    "Island": ["Skagit", "Snohomish"],
    "Jefferson": ["Clallam", "Grays Harbor", "Kitsap", "Mason"],
    "King": ["Kittitas", "Pierce", "Snohomish"],
    "Kitsap": ["Jefferson", "Mason", "Pierce"],
    "Kittitas": ["Chelan", "Grant", "King", "Pierce", "Yakima"],
    "Klickitat": ["Benton", "Skamania", "Yakima"],
    "Lewis": ["Cowlitz", "Grays Harbor", "Pierce", "Thurston", "Wahkiakum", "Yakima"],
    "Lincoln": ["Adams", "Ferry", "Grant", "Spokane", "Stevens", "Whitman"],
    "Mason": ["Grays Harbor", "Jefferson", "Kitsap", "Pierce", "Thurston"],
    "Okanogan": ["Chelan", "Douglas", "Ferry", "Grant"],
    "Pacific": ["Grays Harbor", "Wahkiakum"],
    "Pend Oreille": ["Ferry", "Stevens"],
    "Pierce": ["King", "Kittitas", "Kitsap", "Lewis", "Mason", "Thurston"],
    "San Juan": ["Skagit"],  # Connected by ferry
    "Skagit": ["Island", "San Juan", "Snohomish", "Whatcom"],
    "Skamania": ["Clark", "Cowlitz", "Klickitat"],
    "Snohomish": ["Island", "King", "Skagit", "Whatcom"],
    "Spokane": ["Lincoln", "Stevens", "Whitman"],
    "Stevens": ["Ferry", "Lincoln", "Pend Oreille", "Spokane"],
    "Thurston": ["Grays Harbor", "Lewis", "Mason", "Pierce"],
    "Wahkiakum": ["Cowlitz", "Lewis", "Pacific"],
    "Walla Walla": ["Columbia", "Franklin"],
    "Whatcom": ["Skagit", "Snohomish"],
    "Whitman": ["Adams", "Garfield", "Lincoln", "Spokane"],
    "Yakima": ["Benton", "Kittitas", "Klickitat", "Lewis"]
}

# Drive times between adjacent counties (stored in minutes; functions return seconds)
# Based on typical highway speeds and distances between county centers
county_drive_times = {
    # Format: (county1, county2): minutes
    ("Adams", "Franklin"): 45,
    ("Adams", "Grant"): 35,
    ("Adams", "Lincoln"): 40,
    ("Adams", "Whitman"): 55,
    ("Asotin", "Garfield"): 35,
    ("Benton", "Franklin"): 20,
    ("Benton", "Yakima"): 75,
    ("Benton", "Klickitat"): 90,
    ("Chelan", "Douglas"): 15,
    ("Chelan", "Kittitas"): 65,
    ("Chelan", "Okanogan"): 75,
    ("Clallam", "Jefferson"): 60,
    ("Clark", "Cowlitz"): 45,
    ("Clark", "Skamania"): 50,
    ("Columbia", "Garfield"): 30,
    ("Columbia", "Walla Walla"): 35,
    ("Cowlitz", "Lewis"): 40,
    ("Cowlitz", "Skamania"): 60,
    ("Cowlitz", "Wahkiakum"): 40,
    ("Douglas", "Grant"): 40,
    ("Douglas", "Okanogan"): 85,
    ("Ferry", "Lincoln"): 120,
    ("Ferry", "Okanogan"): 70,
    ("Ferry", "Pend Oreille"): 80,
    ("Ferry", "Stevens"): 45,
    ("Franklin", "Grant"): 50,
    ("Franklin", "Walla Walla"): 55,
    ("Garfield", "Whitman"): 45,
    ("Grant", "Kittitas"): 55,
    ("Grant", "Lincoln"): 50,
    ("Grant", "Okanogan"): 80,
    ("Grays Harbor", "Jefferson"): 75,
    ("Grays Harbor", "Lewis"): 50,
    ("Grays Harbor", "Mason"): 45,
    ("Grays Harbor", "Pacific"): 35,
    ("Grays Harbor", "Thurston"): 60,
    ("Island", "Skagit"): 25,
    ("Island", "Snohomish"): 30,
    ("Jefferson", "Kitsap"): 40,
    ("Jefferson", "Mason"): 55,
    ("King", "Kittitas"): 75,
    ("King", "Pierce"): 35,
    ("King", "Snohomish"): 30,
    ("Kitsap", "Mason"): 30,
    ("Kitsap", "Pierce"): 35,
    ("Kittitas", "Pierce"): 90,
    ("Kittitas", "Yakima"): 45,
    ("Klickitat", "Skamania"): 55,
    ("Klickitat", "Yakima"): 80,
    ("Lewis", "Pierce"): 55,
    ("Lewis", "Thurston"): 45,
    ("Lewis", "Wahkiakum"): 70,
    ("Lewis", "Yakima"): 90,
    ("Lincoln", "Spokane"): 50,
    ("Lincoln", "Stevens"): 65,
    ("Lincoln", "Whitman"): 60,
    ("Mason", "Pierce"): 40,
    ("Mason", "Thurston"): 30,
    ("Okanogan", "Grant"): 95,
    ("Pacific", "Wahkiakum"): 30,
    ("Pend Oreille", "Stevens"): 55,
    ("Pierce", "Thurston"): 30,
    ("San Juan", "Skagit"): 90,  # Includes ferry time
    ("Skagit", "Snohomish"): 35,
    ("Skagit", "Whatcom"): 40,
    ("Snohomish", "Whatcom"): 55,
    ("Spokane", "Stevens"): 60,
    ("Spokane", "Whitman"): 75,
    ("Stevens", "Ferry"): 45,
    ("Stevens", "Pend Oreille"): 55,
}

def get_drive_time(county1, county2):
    """Get drive time between two counties in seconds."""
    key1 = (county1, county2)
    key2 = (county2, county1)
    explicit = county_drive_times.get(key1, county_drive_times.get(key2, None))
    if explicit is not None:
        return int(explicit * 60)

    # Try external routing APIs if keys provided (Google Maps or ORS)
    # Use county centroid coordinates as origin/destination
    google_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    ors_key = os.environ.get('ORS_API_KEY')
    if county1 in county_coords and county2 in county_coords:
        lat1, lon1 = county_coords[county1]
        lat2, lon2 = county_coords[county2]

        # Try Google Maps first
        if google_key:
            try:
                gm_seconds = _query_google_distance_matrix(lat1, lon1, lat2, lon2, google_key)
                if gm_seconds is not None:
                    return gm_seconds
            except Exception:
                pass

        # Try OpenRouteService next
        if ors_key:
            try:
                ors_seconds = _query_ors_matrix(lat1, lon1, lat2, lon2, ors_key)
                if ors_seconds is not None:
                    return ors_seconds
            except Exception:
                pass

        # Fall back to computing an approximate time using haversine distance
        def haversine_km(a_lat, a_lon, b_lat, b_lon):
            R = 6371.0
            phi1 = math.radians(a_lat)
            phi2 = math.radians(b_lat)
            dphi = math.radians(b_lat - a_lat)
            dlambda = math.radians(b_lon - a_lon)
            x = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
            return 2 * R * math.asin(math.sqrt(x))

        dist_km = haversine_km(lat1, lon1, lat2, lon2)
        # apply a larger road-network multiplier for county-to-county distance
        road_multiplier = 1.35
        road_km = dist_km * road_multiplier
        # Average highway speed (km/h) for county-to-county travel
        avg_speed_kmph = 80.0
        hours = road_km / avg_speed_kmph
        seconds = int(max(60, round(hours * 3600)))
        return seconds

    # As a last resort, return a conservative default (90 minutes)
    return 90 * 60