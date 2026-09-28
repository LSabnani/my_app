import os
import json
import re
import random
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "market-trends-secret-v2")

# Memory cache for session data
analysis_cache = {}

# Finviz Industry Slug Mapping
FINVIZ_INDUSTRY_SLUGS = {
    "aerospace & defense": "ind_aerospacedefense,sec_industrials",
    "aerospace and defense": "ind_aerospacedefense,sec_industrials",
    "aerospace": "ind_aerospacedefense,sec_industrials",
    "defense": "ind_aerospacedefense,sec_industrials",
    "defense contractors": "ind_aerospacedefense,sec_industrials",
    "industrials": "ind_aerospacedefense,sec_industrials",
    "broadcasting": "ind_broadcasting,sec_communicationservices",
    "broadcasters": "ind_broadcasting,sec_communicationservices",
    "tv": "ind_broadcasting,sec_communicationservices",
    "television": "ind_broadcasting,sec_communicationservices",
    "news": "ind_broadcasting,sec_communicationservices",
    "media": "ind_entertainment,sec_communicationservices",
    "entertainment": "ind_entertainment,sec_communicationservices",
    "shows": "ind_entertainment,sec_communicationservices",
    "communication services": "ind_entertainment,sec_communicationservices",
    "communications": "ind_entertainment,sec_communicationservices",
    "telecom": "ind_telecomservices,sec_communicationservices",
    "telecom services": "ind_telecomservices,sec_communicationservices",
    "telecommunications": "ind_telecomservices,sec_communicationservices",
    "drug manufacturers general": "ind_drugmanufacturersgeneral,sec_healthcare",
    "drug manufacturers": "ind_drugmanufacturersgeneral,sec_healthcare",
    "drug manufacturer": "ind_drugmanufacturersgeneral,sec_healthcare",
    "pharmaceuticals": "ind_drugmanufacturersgeneral,sec_healthcare",
    "pharmaceutical": "ind_drugmanufacturersgeneral,sec_healthcare",
    "pharma": "ind_drugmanufacturersgeneral,sec_healthcare",
    "healthcare": "ind_drugmanufacturersgeneral,sec_healthcare",
    "biotechnology": "ind_biotechnology,sec_healthcare",
    "biotech": "ind_biotechnology,sec_healthcare",
    "oil & gas integrated": "ind_oilgasintegrated,sec_energy",
    "oil and gas integrated": "ind_oilgasintegrated,sec_energy",
    "oil & gas": "ind_oilgasintegrated,sec_energy",
    "oil and gas": "ind_oilgasintegrated,sec_energy",
    "energy": "ind_oilgasintegrated,sec_energy",
    "petroleum": "ind_oilgasintegrated,sec_energy",
    "semiconductor equipment and materials": "ind_semiconductorequipmentmaterials,sec_technology",
    "semiconductor equipment materials": "ind_semiconductorequipmentmaterials,sec_technology",
    "semiconductor equipment": "ind_semiconductorequipmentmaterials,sec_technology",
    "semiconductor materials": "ind_semiconductorequipmentmaterials,sec_technology",
    "semiconductorequipmentmaterials": "ind_semiconductorequipmentmaterials,sec_technology",
    "semiconductors": "ind_semiconductors,sec_technology",
    "semiconductor": "ind_semiconductors,sec_technology",
    "auto manufacturers": "ind_automanufacturers,sec_consumercyclical",
    "auto manufacturer": "ind_automanufacturers,sec_consumercyclical",
    "automotive": "ind_automanufacturers,sec_consumercyclical",
    "auto": "ind_automanufacturers,sec_consumercyclical",
    "home improvement retail": "ind_homeimprovementretail,sec_consumercyclical",
    "home improvement": "ind_homeimprovementretail,sec_consumercyclical",
    "hardware stores": "ind_homeimprovementretail,sec_consumercyclical",
    "department stores": "ind_departmentstores,sec_consumercyclical",
    "department store": "ind_departmentstores,sec_consumercyclical",
    "lodging": "ind_lodging,sec_consumercyclical",
    "hotels": "ind_lodging,sec_consumercyclical",
    "hotel": "ind_lodging,sec_consumercyclical",
    "resorts": "ind_resortscasinos,sec_consumercyclical",
    "apparel retail": "ind_apparelretail,sec_consumercyclical",
    "specialty retail": "ind_specialtyretail,sec_consumercyclical",
    "discount stores": "ind_discountstores,sec_consumerdefensive",
    "credit services": "ind_creditservices,sec_financial",
    "credit service": "ind_creditservices,sec_financial",
    "credit": "ind_creditservices,sec_financial",
    "financial": "ind_creditservices,sec_financial",
    "financials": "ind_creditservices,sec_financial",
    "payments": "ind_creditservices,sec_financial",
    "software": "ind_softwareapplication,sec_technology",
    "cloud": "ind_softwareinfrastructure,sec_technology",
    "beverages - non-alcoholic": "ind_beveragesnonalcoholic,sec_consumerdefensive",
    "beverages non-alcoholic": "ind_beveragesnonalcoholic,sec_consumerdefensive",
    "non-alcoholic beverages": "ind_beveragesnonalcoholic,sec_consumerdefensive",
    "beverages": "ind_beveragesnonalcoholic,sec_consumerdefensive",
    "soft drinks": "ind_beveragesnonalcoholic,sec_consumerdefensive",
    "beverages - wineries & distilleries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "beverages - wineries and distilleries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "beverages wineries & distilleries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "beverages wineries and distilleries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "wineries & distilleries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "wineries and distilleries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "wineries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "distilleries": "ind_beverageswineriesdistilleries,sec_consumerdefensive",
    "discount stores": "ind_discountstores,sec_consumerdefensive",
    "discount store": "ind_discountstores,sec_consumerdefensive",
    "dollar stores": "ind_discountstores,sec_consumerdefensive",
    "dollar store": "ind_discountstores,sec_consumerdefensive",
    "supercenters": "ind_discountstores,sec_consumerdefensive",
    "warehouse clubs": "ind_discountstores,sec_consumerdefensive",
    "farm products": "ind_farmproducts,sec_consumerdefensive",
    "farm product": "ind_farmproducts,sec_consumerdefensive",
    "agriculture": "ind_farmproducts,sec_consumerdefensive",
    "agricultural": "ind_farmproducts,sec_consumerdefensive",
    "agribusiness": "ind_farmproducts,sec_consumerdefensive",
    "discount stores": "ind_discountstores,sec_consumerdefensive",
    "banking": "ind_banksdiversified,sec_financial"
}

# Static Curated Fallback Database (matching Finviz top market cap rankings)
CURATED_FINVIZ_DB = {
    "ind_farmproducts,sec_consumerdefensive": [
        {"name": "Corteva, Inc. (CTVA)", "share": "32%", "key_offering": "Pure-play agricultural innovator specializing in high-yield seed genetics, crop protection chemistry, and digital farming software", "top_products": ["Pioneer Brand Seed Corn & Soybeans", "Enlist Weed Control System & Chemistry", "Vorceed Enlist Corn Insect Protection Technology"]},
        {"name": "Archer-Daniels-Midland Company (ADM)", "share": "28%", "key_offering": "Global agricultural processing titan operating oilseed crushing, grain merchandising, and human/animal nutrition ingredients", "top_products": ["Crude & Refined Vegetable Oils (Soybean, Canola)", "Biofuels & Industrial Ethanol Solutions", "Specialty Food & Animal Nutrition Ingredients"]},
        {"name": "Bunge Global SA (BG)", "share": "18%", "key_offering": "World leader in oilseed processing, grain sourcing, and sustainable plant-based oil manufacturing for food & bioenergy", "top_products": ["Bulk Soybean & Oilseed Meal Processing", "Plant-Based Specialty Oils & Fats", "Sustainable Biofuel Feedstock Logistics"]},
        {"name": "Tyson Foods, Inc. (TSN)", "share": "14%", "key_offering": "Integrated protein producer operating processing, distribution, and branded chicken, beef, pork, and prepared foods", "top_products": ["Tyson Fresh & Frozen Prepared Chicken", "Jimmy Dean Breakfast Meats & Sandwiches", "Hillshire Farm & Ball Park Brand Products"]},
        {"name": "Darling Ingredients Inc. (DAR)", "share": "8%", "key_offering": "Global leader in converting edible and inedible bio-nutrients into sustainable bio-energy, renewable diesel, and specialty ingredients", "top_products": ["Diamond Green Diesel (DGD) Renewable Fuel", "Gelita Specialty Gelatin & Collagen Peptides", "Nature Safe Organic & Bio-Nutrient Fertilizers"]}
    ],
    "ind_discountstores,sec_consumerdefensive": [
        {"name": "Walmart Inc. (WMT)", "share": "42%", "key_offering": "Global retail superpower operating hypermarkets, Walmart+ subscription, advertising network, and high-efficiency logistics", "top_products": ["Great Value Private Label Grocery & Household Line", "Walmart+ Free Delivery & Shipping Membership", "Equate Health & Personal Care Brand Portfolio"]},
        {"name": "Costco Wholesale Corporation (COST)", "share": "28%", "key_offering": "High-volume membership warehouse club delivering extreme unit value, Kirkland Signature brands, and high loyalty", "top_products": ["Kirkland Signature Premium Food & Household Line", "Costco Executive Membership & Cash-Back Rewards", "Costco Wholesale Grocery & Fuel Services"]},
        {"name": "Target Corporation (TGT)", "share": "14%", "key_offering": "Omnichannel discount retailer combining trendy designer partnerships with essential groceries and Drive Up fulfillment", "top_products": ["Good & Gather Grocery & Favorite Day Brands", "Threshold & Room Essentials Home Furnishings", "Target Circle Loyalty Program & Drive Up Pickup"]},
        {"name": "Dollar General Corporation (DG)", "share": "10%", "key_offering": "Rural discount general merchant delivering small-box neighborhood convenience and consumable goods across 19,000+ stores", "top_products": ["Clover Valley Grocery & Smart Way Budget Line", "DG Fresh Cold Supply Chain Consumables", "Dollar General $1 Value Merchandise Aisle"]},
        {"name": "Dollar Tree, Inc. (DLTR)", "share": "6%", "key_offering": "Fixed-price and multi-price point dollar store operator (Dollar Tree & Family Dollar) serving budget-conscious shoppers", "top_products": ["Dollar Tree $1.25 & $3-$5 Plus Variety Items", "Family Dollar Consumables & Household Cleaners", "Crafter's Square & Seasonal Party Supplies"]}
    ],
    "ind_beverageswineriesdistilleries,sec_consumerdefensive": [
        {"name": "Diageo plc (DEO)", "share": "38%", "key_offering": "World's leading premium spirits distiller operating iconic scotch, tequila, vodka, and gin global brand portfolios", "top_products": ["Johnnie Walker Scotch Whisky & Crown Royal", "Casamigos & Don Julio Premium Tequilas", "Tanqueray Gin, Smirnoff Vodka & Baileys"]},
        {"name": "Constellation Brands, Inc. (STZ)", "share": "28%", "key_offering": "Dominant importer of high-end Mexican beers, ultra-premium Napa wines, and craft spirits across North America", "top_products": ["Modelo Especial & Corona Extra Beer Franchises", "Meiomi & The Prisoner Wine Company Portfolios", "High West Whiskey & Mi CAMPO Tequila"]},
        {"name": "Brown-Forman Corporation (BF-B)", "share": "16%", "key_offering": "Global American whiskey leader, premium tequila, and ready-to-drink (RTD) spirit cocktails", "top_products": ["Jack Daniel's Tennessee Whiskey (Old No. 7)", "Woodford Reserve Super-Premium Bourbon", "Herradura & el Jimador Tequilas"]},
        {"name": "Pernod Ricard SA (PRNDY)", "share": "10%", "key_offering": "Global co-leader in wines & spirits specializing in prestige single malt scotch, cognac, and champagne", "top_products": ["Jameson Irish Whiskey & Chivas Regal Scotch", "Martell Cognac & Glenlivet Single Malt", "Absolut Vodka & Perrier-Jouët Champagne"]},
        {"name": "The Duckhorn Portfolio, Inc. (NAPA)", "share": "8%", "key_offering": "Premier luxury Napa Valley wine producer specializing in estate Cabernet Sauvignon, Merlot, and Pinot Noir", "top_products": ["Duckhorn Vineyards Napa Valley Cabernet", "Decoy Premium California Wine Series", "Kosta Browne & Goldeneye Pinot Noir"]}
    ],
    "ind_beveragesnonalcoholic,sec_consumerdefensive": [
        {"name": "The Coca-Cola Company (KO)", "share": "38%", "key_offering": "Global non-alcoholic concentrate model, sparkling soft drinks, hydration, and ready-to-drink coffee/tea", "top_products": ["Coca-Cola Trademark (Original, Zero Sugar, Diet)", "Sprite, Fanta & Fresca Sparkling Beverages", "Fairlife Ultra-Filtered Milk & BodyArmor Hydration"]},
        {"name": "PepsiCo, Inc. (PEP)", "share": "32%", "key_offering": "Integrated beverage & snack titan with direct-store-delivery (DSD) logistics and global brand scale", "top_products": ["Pepsi-Cola Trademark (Pepsi Zero Sugar, Wild Cherry)", "Gatorade Thirst Quencher & Fast Twitch Energy", "Mountain Dew, Starry & Lipton RTD Teas"]},
        {"name": "Monster Beverage Corporation (MNST)", "share": "14%", "key_offering": "Dominant energy drink brand ecosystem leveraging Coca-Cola's global bottling distribution network", "top_products": ["Monster Energy Original, Ultra & Rehab Lines", "Reign Total Body Fuel & Reign Storm Energy", "Bang Energy & Java Monster Coffee Drinks"]},
        {"name": "Keurig Dr Pepper Inc. (KDP)", "share": "10%", "key_offering": "Leading single-serve coffee system (Keurig) integrated with iconic soft drinks & premium waters", "top_products": ["Dr Pepper Trademark & Cream Soda Series", "Keurig Single-Serve Coffee Pods & Appliances", "Snapple, Core Hydration & Mott's Juices"]},
        {"name": "Celsius Holdings, Inc. (CELH)", "share": "6%", "key_offering": "High-growth functional essential energy drinks for fitness & thermogenic fat burn lifestyle consumers", "top_products": ["Celsius Essential Energy Drinks (Sparkling / Green Tea)", "Celsius On-The-Go Powder Stick Packs", "Celsius Essentials High-Performance Energy Line"]}
    ],
    "ind_broadcasting,sec_communicationservices": [
        {"name": "Fox Corporation (FOXA)", "share": "32%", "key_offering": "Fox News Media, Fox Sports, Fox Broadcasting Network & Tubi streaming service", "top_products": ["Fox News Channel & FOX Business", "Fox Sports Live NFL/College Football Coverage", "Tubi Free Ad-Supported Streaming (FAST) Platform"]},
        {"name": "Paramount Global (PARA)", "share": "24%", "key_offering": "CBS Television Network, Paramount+, Nickelodeon, MTV & CBS News", "top_products": ["CBS Broadcast Network & CBS Sports", "Paramount+ Direct-to-Consumer Streaming", "Nickelodeon & MTV Cable Networks"]},
        {"name": "Nexstar Media Group, Inc. (NXST)", "share": "18%", "key_offering": "The CW Network, NewsNation, antenna TV & largest US local TV broadcast station operator", "top_products": ["NewsNation Cable News Network", "The CW Television Network", "Nexstar Digital & Local TV Stations"]},
        {"name": "Tegna Inc. (TGNA)", "share": "14%", "key_offering": "Major network affiliate stations (CBS, NBC, ABC, FOX) & digital media platforms", "top_products": ["Local NBC/CBS/ABC TV Station Affiliates", "Locked On Podcast Network", "Premion OTT Local Video Advertising"]},
        {"name": "Gray Television, Inc. (GTN)", "share": "12%", "key_offering": "Top-rated local TV stations, local news broadcasting, & regional sports channels", "top_products": ["Gray Local TV Station Portfolio", "Assembly Studios Production Facility", "Local News Live Digital Channel"]}
    ],
    "ind_entertainment,sec_communicationservices": [
        {"name": "The Walt Disney Company (DIS)", "share": "35%", "key_offering": "ABC Television Network, ESPN, Disney+, Hulu, Pixar, Marvel, Lucasfilm & Parks", "top_products": ["ABC Broadcast Network & ESPN Sports", "Disney+ & Hulu Direct-to-Consumer Streaming", "Walt Disney Studios Feature Films & Theme Parks"]},
        {"name": "Netflix, Inc. (NFLX)", "share": "28%", "key_offering": "Global subscription video on demand (SVOD), original series, movies & live events", "top_products": ["Netflix Original Streaming Content", "Netflix Ad-Supported Membership Tier", "Netflix Live Sports & Entertainment Events"]},
        {"name": "Warner Bros. Discovery (WBD)", "share": "18%", "key_offering": "Max streaming service, Warner Bros. Studios, HBO, CNN, TNT Sports & HGTV", "top_products": ["Max Direct-to-Consumer Streaming", "CNN Worldwide News Network", "Warner Bros. Feature Motion Pictures"]},
        {"name": "Live Nation Entertainment (LYV)", "share": "11%", "key_offering": "Ticketmaster live event ticketing, global concert promotion & venue operations", "top_products": ["Ticketmaster Ticketing Platform", "Live Nation Concert Tours & Festivals", "Venue Management & Sponsorship Services"]},
        {"name": "Fox Corporation (FOX)", "share": "8%", "key_offering": "Fox News, Fox Sports, Fox Broadcast Network & Tubi streaming service", "top_products": ["Fox News Channel & FOX Business", "Fox Sports Live Broadcasting", "Tubi Streaming Video Platform"]}
    ],
    "ind_telecomservices,sec_communicationservices": [
        {"name": "Verizon Communications Inc. (VZ)", "share": "38%", "key_offering": "Nationwide 5G Ultra Wideband wireless network, Fios fiber internet & enterprise connectivity", "top_products": ["Verizon Wireless Mobile Voice & Data Plans", "Verizon Fios Gigabit Fiber Internet", "Verizon Business Managed Network Services"]},
        {"name": "AT&T Inc. (T)", "share": "34%", "key_offering": "Nationwide 5G wireless network, AT&T Fiber broadband & business telecommunications", "top_products": ["AT&T 5G Wireless Mobility Services", "AT&T Fiber Multi-Gigabit Broadband", "AT&T Dedicated Business Fiber & Cloud Networking"]},
        {"name": "T-Mobile US, Inc. (TMUS)", "share": "18%", "key_offering": "Ultra Capacity 5G network leader, un-carrier mobile plans & 5G Home Internet", "top_products": ["T-Mobile Magenta & Go5G Mobile Plans", "T-Mobile 5G Fixed Wireless Home Internet", "T-Mobile for Business Enterprise 5G Connectivity"]},
        {"name": "Comcast Corporation (CMCSA)", "share": "6%", "key_offering": "Xfinity broadband internet, NBCUniversal, Peacock, Xfinity Mobile & cable TV", "top_products": ["Xfinity Multi-Gigabit Broadband Internet", "NBCUniversal & Peacock Direct-to-Consumer", "Xfinity Mobile Wireless Service"]},
        {"name": "Charter Communications, Inc. (CHTR)", "share": "4%", "key_offering": "Spectrum Internet, Spectrum Mobile, cable TV & commercial network solutions", "top_products": ["Spectrum High-Speed Cable Broadband", "Spectrum Mobile Converged Wireless", "Spectrum Enterprise Managed Fiber Services"]}
    ],
    "ind_aerospacedefense,sec_industrials": [
        {"name": "General Dynamics Corporation (GD)", "share": "28%", "key_offering": "Gulfstream business jets, Virginia/Columbia-class nuclear submarines, & land combat vehicles", "top_products": ["Gulfstream G700 / G800 Business Jets", "Virginia & Columbia-Class Nuclear Submarines", "M1A2 SEPv3 Abrams Main Battle Tanks"]},
        {"name": "RTX Corporation (RTX)", "share": "24%", "key_offering": "Patriot missile defense systems, Pratt & Whitney GTF engines, & NASAMS air defense", "top_products": ["Patriot MIM-104 Air & Missile Defense", "Pratt & Whitney GTF Aircraft Engines", "NASAMS Air Defense System"]},
        {"name": "Lockheed Martin Corporation (LMT)", "share": "22%", "key_offering": "F-35 Lightning II joint strike fighter, HIMARS rocket artillery, & PAC-3 missile interceptors", "top_products": ["F-35 Lightning II Joint Strike Fighter", "M142 HIMARS Precision Rocket Artillery", "PAC-3 MSE Missile Interceptors"]},
        {"name": "Boeing Company (BA)", "share": "16%", "key_offering": "737/787 commercial jetliners, AH-64 Apache helicopters, & KC-46 aerial refuelers", "top_products": ["737 MAX & 787 Dreamliner Commercial Jets", "AH-64E Apache Attack Helicopters", "KC-46A Pegasus Aerial Refuelers"]},
        {"name": "Northrop Grumman Corporation (NOC)", "share": "10%", "key_offering": "B-21 Raider stealth bomber, Sentinel ICBM, & autonomous unmanned aerial systems (UAS)", "top_products": ["B-21 Raider Stealth Strategic Bomber", "Sentinel LGM-35A ICBM System", "RQ-4 Global Hawk Autonomous UAS"]}
    ],
    "ind_drugmanufacturersgeneral,sec_healthcare": [
        {"name": "Eli Lilly & Co (LLY)", "share": "34%", "key_offering": "Mounjaro / Zepbound GLP-1 receptor agonist therapies & oncology portfolio", "top_products": ["Mounjaro (Tirzepatide Injection)", "Zepbound (Obesity Treatment)", "Verzenio (Oncology Breast Cancer)"]},
        {"name": "Johnson & Johnson (JNJ)", "share": "22%", "key_offering": "Oncology (Darzalex), Immunology (Stelara, Tremfya) & MedTech innovator", "top_products": ["Darzalex (Multiple Myeloma Biologic)", "Stelara (Plaque Psoriasis & IBD)", "Tremfya (IL-23 Inhibitor)"]},
        {"name": "AbbVie Inc (ABBV)", "share": "16%", "key_offering": "Immunology (Skyrizi, Rinvoq, Humira) & Oncology (Imbruvica, Venclexta)", "top_products": ["Skyrizi (IL-23 Inhibitor)", "Rinvoq (JAK Inhibitor)", "Humira (TNF-Alpha Blocker)"]},
        {"name": "Merck & Co Inc (MRK)", "share": "14%", "key_offering": "Keytruda immuno-oncology blockbuster, GARDASIL HPV vaccines & WINREVAIR", "top_products": ["Keytruda (Anti-PD-1 Immuno-Oncology)", "GARDASIL 9 (HPV Vaccine)", "WINREVAIR (Pulmonary Arterial Hypertension)"]},
        {"name": "Novartis AG (NVS)", "share": "10%", "key_offering": "Entresto cardiovascular, Cosentyx immunology & Pluvicto radioligand therapies", "top_products": ["Entresto (Heart Failure Therapy)", "Cosentyx (Secukinumab Biologic)", "Pluvicto (Radioligand Therapy)"]}
    ],
    "ind_oilgasintegrated,sec_energy": [
        {"name": "Exxon Mobil Corporation (XOM)", "share": "36%", "key_offering": "Permian Basin low-cost scale, Guyana deepwater & global refining/chemical integration", "top_products": ["Permian Basin Low-Cost Unconventional Crude", "Guyana Offshore Deepwater Production", "Mobil 1 Synthetic Lubricants & Chemicals"]},
        {"name": "Chevron Corporation (CVX)", "share": "28%", "key_offering": "Tengizchevroil expansion, deepwater Gulf of Mexico & accretive asset integration", "top_products": ["Tengizchevroil Future Growth Project Crude", "Gulf of Mexico Deepwater Anchor Platform", "Chevron Renewable Clean Fuels"]},
        {"name": "Shell plc (SHEL)", "share": "16%", "key_offering": "Global LNG trading dominance, deepwater production & integrated energy marketing", "top_products": ["Global LNG Integrated Trading & Shipping", "Deepwater Gulf of Mexico / Brazil Assets", "Shell Recharge EV Charging Network"]},
        {"name": "TotalEnergies SE (TTE)", "share": "11%", "key_offering": "Multi-energy strategy spanning LNG, upstream oil & renewable power infrastructure", "top_products": ["Global Integrated LNG Export Supply", "Offshore Deepwater Upstream Oil", "TotalEnergies Renewable Solar & Wind Infrastructure"]},
        {"name": "BP p.l.c. (BP)", "share": "9%", "key_offering": "Resilient upstream oil & gas production, global refining & bioenergy integration", "top_products": ["Upstream Deepwater Oil & Gas Production", "Whiting & Cherry Point Refining Operations", "BP Pulse EV Rapid Charging Network"]}
    ],
    "ind_homeimprovementretail,sec_consumercyclical": [
        {"name": "The Home Depot, Inc. (HD)", "share": "28%", "key_offering": "Largest US home improvement retailer (Pro Extra ecosystem, HD Supply MRO & private tool brands)", "top_products": ["Home Depot Pro Extra Contractor Platform", "Husky & Rigid Professional Tools", "HD Supply Maintenance & MRO Distribution"]},
        {"name": "Lowe's Companies, Inc. (LOW)", "share": "17%", "key_offering": "Home improvement retail scale (Lowe's MVPs Pro Rewards, Kobalt tools & total home service)", "top_products": ["Lowe's MVPs Pro Rewards Program", "Kobalt & Craftsman Tools Portfolio", "Lowe's Installation & Total Home Services"]},
        {"name": "Floor & Decor Holdings, Inc. (FND)", "share": "6%", "key_offering": "Specialty hard-surface flooring retailer (tile, wood, stone) offering warehouse-format scale", "top_products": ["Hard-Surface Tile & Natural Stone Flooring", "Rigid Core Luxury Vinyl Plank (LVP)", "Pro Premier Flooring Installation Supplies"]},
        {"name": "Tractor Supply Company (TSCO)", "share": "5%", "key_offering": "Rural lifestyle, land maintenance, lawn & garden, and livestock supply retail chain", "top_products": ["Neighbor's Club Rural Loyalty Program", "CountyLine Farm & Fencing Equipment", "4Knines & Ranch Hardware Supplies"]},
        {"name": "Leslies, Inc. (LESL)", "share": "2%", "key_offering": "Leading specialty pool and spa care product retailer, chemicals, & maintenance services", "top_products": ["Leslie's Pool Chemicals & Water Testing", "Residential Pool Equipment & Pumps", "Leslie's On-Site Pool Repair Services"]}
    ],
    "ind_lodging,sec_consumercyclical": [
        {"name": "Marriott International, Inc. (MAR)", "share": "36%", "key_offering": "Asset-light hotel franchisor (Marriott, Ritz-Carlton, Sheraton) & Marriott Bonvoy loyalty ecosystem", "top_products": ["Marriott Bonvoy Global Loyalty Platform", "Luxury & Premium Hotel Franchising (Ritz-Carlton, St. Regis)", "Select Service Hotel Brands (Courtyard, Residence Inn)"]},
        {"name": "Hilton Worldwide Holdings Inc. (HLT)", "share": "28%", "key_offering": "Asset-light hotel franchising (Hilton, Waldorf Astoria, Hampton) & Hilton Honors digital ecosystem", "top_products": ["Hilton Honors Loyalty Platform & Direct Booking App", "Hilton Hotels & Resorts Full-Service Properties", "Hampton by Hilton & Hilton Garden Inn Select Service"]},
        {"name": "Hyatt Hotels Corporation (H)", "share": "18%", "key_offering": "Luxury, lifestyle, & all-inclusive resort management (Park Hyatt, Andaz, World of Hyatt)", "top_products": ["World of Hyatt Global Member Loyalty Platform", "Park Hyatt & Grand Hyatt Ultra-Luxury Properties", "Hyatt Ziva & Zilara All-Inclusive Resort Portfolio"]},
        {"name": "Host Hotels & Resorts, Inc. (HST)", "share": "10%", "key_offering": "Premier lodging Real Estate Investment Trust (REIT) owning luxury & upper-upscale hotel properties", "top_products": ["Luxury Urban Hotel Real Estate Portfolio", "Sunbelt Resort Real Estate Assets", "Host Hotels Capital Asset Enhancement Projects"]},
        {"name": "Wyndham Hotels & Resorts, Inc. (WH)", "share": "8%", "key_offering": "World's largest hotel franchising company by store count specializing in economy & midscale lodging", "top_products": ["Wyndham Rewards Loyalty Platform", "Days Inn, Super 8 & Ramada Hotel Brands", "Wyndham Connect Hotel Management System"]}
    ],
    "ind_departmentstores,sec_consumercyclical": [
        {"name": "The TJX Companies, Inc. (TJX)", "share": "38%", "key_offering": "Off-price apparel & home fashion (T.J. Maxx, Marshalls, HomeGoods) & treasure-hunt retail model", "top_products": ["T.J. Maxx & Marshalls Off-Price Apparel", "HomeGoods & Homesense Home Decor", "Sierra Outdoor & Activewear Stores"]},
        {"name": "Macy's, Inc. (M)", "share": "24%", "key_offering": "Omnichannel department stores (Macy's, Bloomingdale's, Bluemercury) & exclusive fashion partnerships", "top_products": ["Macy's Department Store & E-Commerce", "Bloomingdale's Luxury Department Stores", "Bluemercury Beauty & Skincare Specialty"]},
        {"name": "Kohl's Corporation (KSS)", "share": "16%", "key_offering": "Omnichannel department stores, Sephora at Kohl's beauty shop-in-shops & private fashion labels", "top_products": ["Sephora at Kohl's Beauty Shop-in-Shops", "Kohl's Exclusive & Private Apparel Brands", "Kohl's Cash Loyalty Program & Credit"]},
        {"name": "Nordstrom, Inc. (JWN)", "share": "12%", "key_offering": "Luxury upscale department stores (Nordstrom) & off-price retail channels (Nordstrom Rack)", "top_products": ["Nordstrom Full-Line Upscale Department Stores", "Nordstrom Rack Off-Price Retail Outlets", "Nordstrom Anniversary Sale & Personal Styling"]},
        {"name": "Dillard's, Inc. (DDS)", "share": "10%", "key_offering": "Regional department store chain specializing in premium apparel, cosmetics, & home furnishings", "top_products": ["Dillard's Exclusive Brand Apparel", "Dillard's Cosmetics & Beauty Counters", "Dillard's Home & Fashion Accessories"]}
    ],
    "ind_automanufacturers,sec_consumercyclical": [
        {"name": "Tesla, Inc. (TSLA)", "share": "38%", "key_offering": "Full Self-Driving (FSD) neural net, Megapack energy, 4680 cells & EV market leader", "top_products": ["Model Y / Model 3 Electric Vehicles", "Full Self-Driving (FSD) Neural Network", "Megapack Commercial Energy Storage"]},
        {"name": "Toyota Motor Corp (TM)", "share": "24%", "key_offering": "Global hybrid volume leader, Toyota Production System (TPS) & solid-state battery R&D", "top_products": ["Toyota RAV4 & Prius Hybrid Powertrains", "Toyota Production System (TPS) Automotive Scale", "Lexus Luxury Electrified Vehicles"]},
        {"name": "General Motors Company (GM)", "share": "15%", "key_offering": "Ultium EV architecture, Super Cruise hands-free driving & BrightDrop commercial fleet", "top_products": ["Chevrolet Silverado & Equinox Ultium EVs", "Super Cruise Autonomous Highway Driving", "BrightDrop Commercial Electric Vans"]},
        {"name": "Ferrari N.V. (RACE)", "share": "11%", "key_offering": "Ultra-luxury high-margin sports cars, hybrid V8/V12 powertrains & brand equity", "top_products": ["Ferrari SF90 Stradale Hybrid Supercar", "Purosangue V12 High-Performance SUV", "296 GTB Plug-In Hybrid Sports Car"]},
        {"name": "Ford Motor Company (F)", "share": "8%", "key_offering": "F-150 Lightning EV truck, Mustang Mach-E & Ford Pro commercial software", "top_products": ["F-150 Lightning & Commercial Power Trucks", "Mustang Mach-E Electric Crossover", "Ford Pro Fleet Management Telematics"]}
    ],
    "ind_creditservices,sec_financial": [
        {"name": "Visa Inc. (V)", "share": "38%", "key_offering": "Global payment network, tokenization security & transaction processing infrastructure", "top_products": ["VisaNet Global Clearing & Authorization Network", "Visa Token Service (VTS) Security Infrastructure", "Visa Direct Real-Time P2P Payments"]},
        {"name": "Mastercard Incorporated (MA)", "share": "32%", "key_offering": "Global payment processing, Cyber & Intelligence solutions & open banking network", "top_products": ["Mastercard Integrated Processing Network", "Cyber & Intelligence Fraud Solutions", "Mastercard Open Banking & API Gateway"]},
        {"name": "American Express Company (AXP)", "share": "14%", "key_offering": "Premium closed-loop credit network, travel rewards & merchant acquisition", "top_products": ["Centurion / Platinum Premium Credit Cards", "Merchant Closed-Loop Network Processing", "Amex Express Rewards & Travel Services"]},
        {"name": "PayPal Holdings, Inc. (PYPL)", "share": "9%", "key_offering": "Branded digital checkout, Venmo P2P payments & merchant payment gateway", "top_products": ["Branded PayPal Digital Express Checkout", "Venmo Social Peer-to-Peer Wallet", "Braintree Merchant Payment Gateway"]},
        {"name": "Capital One Financial Corp (COF)", "share": "7%", "key_offering": "Consumer credit card issuing, digital banking platform & auto lending", "top_products": ["Venture X & Spark Business Credit Cards", "Capital One 360 Digital Banking", "Capital One Auto Navigator Lending"]}
    ],
    "ind_semiconductorequipmentmaterials,sec_technology": [
        {"name": "ASML Holding N.V. (ASML)", "share": "38%", "key_offering": "Monopolistic EUV (Extreme Ultraviolet) & High-NA lithography systems for sub-3nm nodes", "top_products": ["Twinscan EXE High-NA EUV Lithography", "Twinscan NXE 0.33 NA EUV Systems", "YieldStar Optical Metrology & Inspection"]},
        {"name": "Applied Materials (AMAT)", "share": "26%", "key_offering": "Broadest materials engineering, chemical/physical vapor deposition (CVD/PVD) & planarization", "top_products": ["Centura & Endura Thin Film PVD Systems", "Producer Chemical Vapor Deposition (CVD)", "VeritySEM Inline Metrology & Inspection"]},
        {"name": "Lam Research Corp (LRCX)", "share": "19%", "key_offering": "Dominant high-aspect-ratio wafer etching and selective deposition for 3D NAND & logic", "top_products": ["Vector High-Aspect-Ratio Etch Systems", "ALTUS Tungsten / 3D NAND Deposition", "Kiyo Conductor Wafer Etching Platforms"]},
        {"name": "KLA Corporation (KLAC)", "share": "12%", "key_offering": "World-leading process control, optical wafer inspection, metrology & yield management", "top_products": ["KLA 39xx Broadband Optical Inspection", "Voyager Wafer Defect Inspection Systems", "5D Analyzer Process Control Metrology"]}
    ],
    "ind_semiconductors,sec_technology": [
        {"name": "NVIDIA Corporation (NVDA)", "share": "45%", "key_offering": "Blackwell/H100 AI GPUs, CUDA software stack & Quantum InfiniBand networking", "top_products": ["Blackwell / H100 Tensor Core GPUs", "CUDA Parallel Computing Software Stack", "Quantum-2 InfiniBand Networking"]},
        {"name": "Taiwan Semiconductor (TSMC)", "share": "32%", "key_offering": "World's largest pure-play foundry manufacturing >90% of advanced sub-5nm chips", "top_products": ["N3 / N3E 3nm Advanced Node Foundry Wafers", "CoWoS Advanced 3D Packaging", "N4P 4nm HPC Semiconductor Processing"]},
        {"name": "Broadcom Inc. (AVGO)", "share": "14%", "key_offering": "Custom AI ASICs, high-speed Tomahawk Ethernet switches & RF front-end modules", "top_products": ["Tomahawk 5 51.2Tbps Ethernet Switches", "Jericho3-AI Fabric Routers", "Custom AI ASIC Accelerator Engines"]}
    ]
}

def fetch_finviz_top_companies(industry_slug):
    """
    Attempts live fetch of Finviz top market cap companies for the given industry/country slug.
    Falls back to curated database if network request fails or returns empty.
    """
    url = f"https://finviz.com/screener.ashx?v=111&f={industry_slug}&o=-marketcap"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            matches = re.findall(r'data-boxover-ticker="([^"]+)"[^>]*data-boxover-company="([^"]+)"', res.text)
            seen = set()
            companies = []
            for ticker, comp in matches:
                comp_clean = comp.replace('&amp;', '&').replace('&quot;', '"')
                if ticker not in seen:
                    seen.add(ticker)
                    companies.append({"ticker": ticker, "company": comp_clean})
            
            if companies:
                return companies
    except Exception as e:
        print(f"Finviz live fetch fallback used: {e}")
        
    return None

def lookup_finviz_ticker(ticker):
    """
    Scrapes finviz.com for a given ticker symbol to find its Sector, Industry, and Country filter,
    then fetches competitors in that industry/country by market cap and selects 2 above and 2 below the target ticker.
    """
    ticker_clean = ticker.strip().upper()
    url = f"https://finviz.com/quote.ashx?t={ticker_clean}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    sector = ""
    industry = ""
    industry_slug = None
    geo_slug = ""
    
    # Pre-populated curated fallback lookup for common tickers
    TICKER_FALLBACKS = {
        "LMT": {"company": "Lockheed Martin Corp", "sector": "Industrials", "industry": "Aerospace & Defense", "slug": "geo_usa,ind_aerospacedefense,sec_industrials"},
        "RTX": {"company": "RTX Corp", "sector": "Industrials", "industry": "Aerospace & Defense", "slug": "geo_usa,ind_aerospacedefense,sec_industrials"},
        "GD": {"company": "General Dynamics Corp", "sector": "Industrials", "industry": "Aerospace & Defense", "slug": "geo_usa,ind_aerospacedefense,sec_industrials"},
        "BA": {"company": "Boeing Co", "sector": "Industrials", "industry": "Aerospace & Defense", "slug": "geo_usa,ind_aerospacedefense,sec_industrials"},
        "NOC": {"company": "Northrop Grumman Corp", "sector": "Industrials", "industry": "Aerospace & Defense", "slug": "geo_usa,ind_aerospacedefense,sec_industrials"},
        "INTC": {"company": "Intel Corp", "sector": "Technology", "industry": "Semiconductors", "slug": "geo_usa,ind_semiconductors,sec_technology"},
        "XOM": {"company": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated", "slug": "geo_usa,ind_oilgasintegrated,sec_energy"},
        "CVX": {"company": "Chevron Corporation", "sector": "Energy", "industry": "Oil & Gas Integrated", "slug": "geo_usa,ind_oilgasintegrated,sec_energy"},
        "SHEL": {"company": "Shell plc", "sector": "Energy", "industry": "Oil & Gas Integrated", "slug": "ind_oilgasintegrated,sec_energy"},
        "TTE": {"company": "TotalEnergies SE", "sector": "Energy", "industry": "Oil & Gas Integrated", "slug": "ind_oilgasintegrated,sec_energy"},
        "BP": {"company": "BP p.l.c.", "sector": "Energy", "industry": "Oil & Gas Integrated", "slug": "ind_oilgasintegrated,sec_energy"},
        "V": {"company": "Visa Inc.", "sector": "Financial", "industry": "Credit Services", "slug": "geo_usa,ind_creditservices,sec_financial"},
        "MA": {"company": "Mastercard Incorporated", "sector": "Financial", "industry": "Credit Services", "slug": "geo_usa,ind_creditservices,sec_financial"},
        "AXP": {"company": "American Express Co", "sector": "Financial", "industry": "Credit Services", "slug": "geo_usa,ind_creditservices,sec_financial"},
        "PYPL": {"company": "PayPal Holdings Inc", "sector": "Financial", "industry": "Credit Services", "slug": "geo_usa,ind_creditservices,sec_financial"},
        "COF": {"company": "Capital One Financial Corp", "sector": "Financial", "industry": "Credit Services", "slug": "geo_usa,ind_creditservices,sec_financial"},
        "TSLA": {"company": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "slug": "geo_usa,ind_automanufacturers,sec_consumercyclical"},
        "TM": {"company": "Toyota Motor Corp", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "slug": "ind_automanufacturers,sec_consumercyclical"},
        "GM": {"company": "General Motors", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "slug": "geo_usa,ind_automanufacturers,sec_consumercyclical"},
        "F": {"company": "Ford Motor Co", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "slug": "geo_usa,ind_automanufacturers,sec_consumercyclical"},
        "LLY": {"company": "Eli Lilly & Co", "sector": "Healthcare", "industry": "Drug Manufacturers - General", "slug": "geo_usa,ind_drugmanufacturersgeneral,sec_healthcare"},
        "JNJ": {"company": "Johnson & Johnson", "sector": "Healthcare", "industry": "Drug Manufacturers - General", "slug": "geo_usa,ind_drugmanufacturersgeneral,sec_healthcare"},
        "ABBV": {"company": "AbbVie Inc", "sector": "Healthcare", "industry": "Drug Manufacturers - General", "slug": "geo_usa,ind_drugmanufacturersgeneral,sec_healthcare"},
        "MRK": {"company": "Merck & Co Inc", "sector": "Healthcare", "industry": "Drug Manufacturers - General", "slug": "geo_usa,ind_drugmanufacturersgeneral,sec_healthcare"},
        "NVS": {"company": "Novartis AG", "sector": "Healthcare", "industry": "Drug Manufacturers - General", "slug": "ind_drugmanufacturersgeneral,sec_healthcare"},
        "ASML": {"company": "ASML Holding NV", "sector": "Technology", "industry": "Semiconductor Equipment & Materials", "slug": "ind_semiconductorequipmentmaterials,sec_technology"},
        "AMAT": {"company": "Applied Materials", "sector": "Technology", "industry": "Semiconductor Equipment & Materials", "slug": "geo_usa,ind_semiconductorequipmentmaterials,sec_technology"},
        "LRCX": {"company": "Lam Research", "sector": "Technology", "industry": "Semiconductor Equipment & Materials", "slug": "geo_usa,ind_semiconductorequipmentmaterials,sec_technology"},
        "KLAC": {"company": "KLA Corp", "sector": "Technology", "industry": "Semiconductor Equipment & Materials", "slug": "geo_usa,ind_semiconductorequipmentmaterials,sec_technology"},
        "NVDA": {"company": "NVIDIA Corp", "sector": "Technology", "industry": "Semiconductors", "slug": "geo_usa,ind_semiconductors,sec_technology"},
        "AAPL": {"company": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "slug": "geo_usa,ind_consumerelectronics,sec_technology"},
        "MSFT": {"company": "Microsoft Corp.", "sector": "Technology", "industry": "Software - Infrastructure", "slug": "geo_usa,ind_softwareinfrastructure,sec_technology"},
        "AMZN": {"company": "Amazon.com Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail", "slug": "geo_usa,ind_internetretail,sec_consumercyclical"},
        "GOOGL": {"company": "Alphabet Inc.", "sector": "Communication Services", "industry": "Internet Content & Information", "slug": "geo_usa,ind_internetcontentinformation,sec_communicationservices"},
        "FOXA": {"company": "Fox Corporation (Class A)", "sector": "Communication Services", "industry": "Broadcasting", "slug": "geo_usa,ind_broadcasting,sec_communicationservices"},
        "FOX": {"company": "Fox Corporation (Class B)", "sector": "Communication Services", "industry": "Broadcasting", "slug": "geo_usa,ind_broadcasting,sec_communicationservices"},
        "PARA": {"company": "Paramount Global", "sector": "Communication Services", "industry": "Broadcasting", "slug": "geo_usa,ind_broadcasting,sec_communicationservices"},
        "NXST": {"company": "Nexstar Media Group, Inc.", "sector": "Communication Services", "industry": "Broadcasting", "slug": "geo_usa,ind_broadcasting,sec_communicationservices"},
        "TGNA": {"company": "Tegna Inc.", "sector": "Communication Services", "industry": "Broadcasting", "slug": "geo_usa,ind_broadcasting,sec_communicationservices"},
        "GTN": {"company": "Gray Television, Inc.", "sector": "Communication Services", "industry": "Broadcasting", "slug": "geo_usa,ind_broadcasting,sec_communicationservices"},
        "DIS": {"company": "The Walt Disney Company", "sector": "Communication Services", "industry": "Entertainment", "slug": "geo_usa,ind_entertainment,sec_communicationservices"},
        "NFLX": {"company": "Netflix, Inc.", "sector": "Communication Services", "industry": "Entertainment", "slug": "geo_usa,ind_entertainment,sec_communicationservices"},
        "WBD": {"company": "Warner Bros. Discovery", "sector": "Communication Services", "industry": "Entertainment", "slug": "geo_usa,ind_entertainment,sec_communicationservices"},
        "LYV": {"company": "Live Nation Entertainment", "sector": "Communication Services", "industry": "Entertainment", "slug": "geo_usa,ind_entertainment,sec_communicationservices"},
        "TJX": {"company": "The TJX Companies, Inc.", "sector": "Consumer Cyclical", "industry": "Department Stores", "slug": "geo_usa,ind_departmentstores,sec_consumercyclical"},
        "M": {"company": "Macy's, Inc.", "sector": "Consumer Cyclical", "industry": "Department Stores", "slug": "geo_usa,ind_departmentstores,sec_consumercyclical"},
        "KSS": {"company": "Kohl's Corporation", "sector": "Consumer Cyclical", "industry": "Department Stores", "slug": "geo_usa,ind_departmentstores,sec_consumercyclical"},
        "JWN": {"company": "Nordstrom, Inc.", "sector": "Consumer Cyclical", "industry": "Department Stores", "slug": "geo_usa,ind_departmentstores,sec_consumercyclical"},
        "DDS": {"company": "Dillard's, Inc.", "sector": "Consumer Cyclical", "industry": "Department Stores", "slug": "geo_usa,ind_departmentstores,sec_consumercyclical"},
        "MAR": {"company": "Marriott International, Inc.", "sector": "Consumer Cyclical", "industry": "Lodging", "slug": "geo_usa,ind_lodging,sec_consumercyclical"},
        "HLT": {"company": "Hilton Worldwide Holdings Inc.", "sector": "Consumer Cyclical", "industry": "Lodging", "slug": "geo_usa,ind_lodging,sec_consumercyclical"},
        "H": {"company": "Hyatt Hotels Corporation", "sector": "Consumer Cyclical", "industry": "Lodging", "slug": "geo_usa,ind_lodging,sec_consumercyclical"},
        "HST": {"company": "Host Hotels & Resorts, Inc.", "sector": "Consumer Cyclical", "industry": "Lodging", "slug": "geo_usa,ind_lodging,sec_consumercyclical"},
        "WH": {"company": "Wyndham Hotels & Resorts, Inc.", "sector": "Consumer Cyclical", "industry": "Lodging", "slug": "geo_usa,ind_lodging,sec_consumercyclical"},
        "HD": {"company": "The Home Depot, Inc.", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail", "slug": "geo_usa,ind_homeimprovementretail,sec_consumercyclical"},
        "LOW": {"company": "Lowe's Companies, Inc.", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail", "slug": "geo_usa,ind_homeimprovementretail,sec_consumercyclical"},
        "FND": {"company": "Floor & Decor Holdings, Inc.", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail", "slug": "geo_usa,ind_homeimprovementretail,sec_consumercyclical"},
        "TSCO": {"company": "Tractor Supply Company", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail", "slug": "geo_usa,ind_homeimprovementretail,sec_consumercyclical"},
        "LESL": {"company": "Leslie's, Inc.", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail", "slug": "geo_usa,ind_homeimprovementretail,sec_consumercyclical"},
        "KO": {"company": "The Coca-Cola Company", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic", "slug": "geo_usa,ind_beveragesnonalcoholic,sec_consumerdefensive"},
        "PEP": {"company": "PepsiCo, Inc.", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic", "slug": "geo_usa,ind_beveragesnonalcoholic,sec_consumerdefensive"},
        "MNST": {"company": "Monster Beverage Corporation", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic", "slug": "geo_usa,ind_beveragesnonalcoholic,sec_consumerdefensive"},
        "KDP": {"company": "Keurig Dr Pepper Inc.", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic", "slug": "geo_usa,ind_beveragesnonalcoholic,sec_consumerdefensive"},
        "CELH": {"company": "Celsius Holdings, Inc.", "sector": "Consumer Defensive", "industry": "Beverages - Non-Alcoholic", "slug": "geo_usa,ind_beveragesnonalcoholic,sec_consumerdefensive"},
        "DEO": {"company": "Diageo plc", "sector": "Consumer Defensive", "industry": "Beverages - Wineries & Distilleries", "slug": "ind_beverageswineriesdistilleries,sec_consumerdefensive"},
        "STZ": {"company": "Constellation Brands, Inc.", "sector": "Consumer Defensive", "industry": "Beverages - Wineries & Distilleries", "slug": "geo_usa,ind_beverageswineriesdistilleries,sec_consumerdefensive"},
        "BF-B": {"company": "Brown-Forman Corporation", "sector": "Consumer Defensive", "industry": "Beverages - Wineries & Distilleries", "slug": "geo_usa,ind_beverageswineriesdistilleries,sec_consumerdefensive"},
        "PRNDY": {"company": "Pernod Ricard SA", "sector": "Consumer Defensive", "industry": "Beverages - Wineries & Distilleries", "slug": "ind_beverageswineriesdistilleries,sec_consumerdefensive"},
        "NAPA": {"company": "The Duckhorn Portfolio, Inc.", "sector": "Consumer Defensive", "industry": "Beverages - Wineries & Distilleries", "slug": "geo_usa,ind_beverageswineriesdistilleries,sec_consumerdefensive"},
        "WMT": {"company": "Walmart Inc.", "sector": "Consumer Defensive", "industry": "Discount Stores", "slug": "geo_usa,ind_discountstores,sec_consumerdefensive"},
        "COST": {"company": "Costco Wholesale Corporation", "sector": "Consumer Defensive", "industry": "Discount Stores", "slug": "geo_usa,ind_discountstores,sec_consumerdefensive"},
        "TGT": {"company": "Target Corporation", "sector": "Consumer Defensive", "industry": "Discount Stores", "slug": "geo_usa,ind_discountstores,sec_consumerdefensive"},
        "DG": {"company": "Dollar General Corporation", "sector": "Consumer Defensive", "industry": "Discount Stores", "slug": "geo_usa,ind_discountstores,sec_consumerdefensive"},
        "DLTR": {"company": "Dollar Tree, Inc.", "sector": "Consumer Defensive", "industry": "Discount Stores", "slug": "geo_usa,ind_discountstores,sec_consumerdefensive"},
        "CTVA": {"company": "Corteva, Inc.", "sector": "Consumer Defensive", "industry": "Farm Products", "slug": "geo_usa,ind_farmproducts,sec_consumerdefensive"},
        "ADM": {"company": "Archer-Daniels-Midland Company", "sector": "Consumer Defensive", "industry": "Farm Products", "slug": "geo_usa,ind_farmproducts,sec_consumerdefensive"},
        "BG": {"company": "Bunge Global SA", "sector": "Consumer Defensive", "industry": "Farm Products", "slug": "geo_usa,ind_farmproducts,sec_consumerdefensive"},
        "TSN": {"company": "Tyson Foods, Inc.", "sector": "Consumer Defensive", "industry": "Farm Products", "slug": "geo_usa,ind_farmproducts,sec_consumerdefensive"},
        "DAR": {"company": "Darling Ingredients Inc.", "sector": "Consumer Defensive", "industry": "Farm Products", "slug": "geo_usa,ind_farmproducts,sec_consumerdefensive"}
    }

    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            sec_match = re.search(r'href="screener(?:\.ashx)?\?v=111&(?:amp;)?f=(sec_[^"]+)"[^>]*>([^<]+)</a>', res.text)
            ind_match = re.search(r'href="screener(?:\.ashx)?\?v=111&(?:amp;)?f=(ind_[^"]+)"[^>]*>(?:<span[^>]*>)?([^<]+)', res.text)
            geo_match = re.search(r'href="screener(?:\.ashx)?\?v=111&(?:amp;)?f=(geo_[^"]+)"', res.text)

            if geo_match:
                geo_slug = geo_match.group(1).strip()

            if sec_match:
                sec_slug = sec_match.group(1).strip()
                sector = sec_match.group(2).strip()
            else:
                sec_slug = ""

            if ind_match:
                ind_slug = ind_match.group(1).strip()
                industry = ind_match.group(2).strip()
            else:
                ind_slug = ""

            slug_parts = []
            if geo_slug:
                slug_parts.append(geo_slug)
            if ind_slug:
                slug_parts.append(ind_slug)
            if sec_slug:
                slug_parts.append(sec_slug)
            if slug_parts:
                industry_slug = ",".join(slug_parts)
    except Exception as e:
        print(f"Finviz web scraper lookup exception for {ticker_clean}: {e}")

    if not sector or not industry:
        if ticker_clean in TICKER_FALLBACKS:
            fb = TICKER_FALLBACKS[ticker_clean]
            sector = fb["sector"]
            industry = fb["industry"]
            industry_slug = fb["slug"]
        else:
            sector = "Financial" if ticker_clean in ["V", "MA", "AXP", "PYPL"] else "General Industry"
            industry = "Credit Services" if ticker_clean in ["V", "MA", "AXP", "PYPL"] else f"Sector for {ticker_clean}"
            industry_slug = "geo_usa,ind_creditservices,sec_financial" if ticker_clean in ["V", "MA", "AXP", "PYPL"] else "geo_usa,ind_drugmanufacturersgeneral,sec_healthcare"

    if not industry_slug:
        industry_slug = FINVIZ_INDUSTRY_SLUGS.get(industry.lower(), "geo_usa,ind_creditservices,sec_financial" if "credit" in industry.lower() or "financial" in sector.lower() else "geo_usa,ind_drugmanufacturersgeneral,sec_healthcare")

    # Fetch top companies
    top_raw = fetch_finviz_top_companies(industry_slug)
    selected_raw = []

    if top_raw:
        # Find position of target ticker for 2-above / 2-below market cap windowing
        target_idx = -1
        for idx, c in enumerate(top_raw):
            if c['ticker'].upper() == ticker_clean:
                target_idx = idx
                break
        
        if target_idx != -1 and len(top_raw) >= 5:
            start_idx = max(0, target_idx - 2)
            end_idx = start_idx + 5
            if end_idx > len(top_raw):
                end_idx = len(top_raw)
                start_idx = max(0, end_idx - 5)
            selected_raw = top_raw[start_idx:end_idx]
        else:
            selected_raw = top_raw[:5]

    if not selected_raw:
        if industry_slug in CURATED_FINVIZ_DB:
            competitors = CURATED_FINVIZ_DB[industry_slug]
        else:
            competitors = resolve_market_leaders(sector, industry)
    else:
        shares = ["38%", "32%", "14%", "9%", "7%"]
        offerings_map = {
            "V": "Global payment network, tokenization security & transaction processing infrastructure",
            "MA": "Global payment processing, Cyber & Intelligence solutions & open banking network",
            "AXP": "Premium closed-loop credit network, travel rewards & merchant acquisition",
            "PYPL": "Branded digital checkout, Venmo P2P payments & merchant payment gateway",
            "COF": "Consumer credit card issuing, digital banking platform & auto lending",
            "INTC": "x86 CPUs, Foundry Services (IFS), Xeon server chips & Client Computing",
            "AMD": "EPYC server processors, Ryzen desktop/mobile CPUs & Instinct AI accelerators",
            "MU": "High-Bandwidth Memory (HBM3E), DRAM memory modules & NAND flash storage",
            "TXN": "Analog signal chain chips, embedded microcontrollers & power management ICs",
            "MRVL": "Custom AI ASICs, optical DSP interconnects & data center storage controllers",
            "NFLX": "Pure-play subscription video-on-demand (SVOD) leader with global original content, ad-tier, & live streaming",
            "DIS": "Integrated media titan spanning ABC TV network, ESPN live sports, Disney+/Hulu streaming, Pixar/Marvel IP & Parks",
            "WBD": "Max streaming service, Warner Bros. film/TV studios, HBO premium cable, CNN news & TNT Sports",
            "LYV": "Global leader in live event promotion, venue operations, and Ticketmaster primary/secondary ticketing platform",
            "FOXA": "Fox News Media, Fox Sports live broadcasting, Fox broadcast network & Tubi free ad-supported streaming (FAST)",
            "FOX": "Fox News Channel, Fox Business, Fox Sports live events & Tubi streaming video platform",
            "PARA": "CBS Television Network, Paramount+ direct-to-consumer streaming, CBS News, Nickelodeon & MTV cable networks",
            "TKO": "UFC combat sports & WWE sports entertainment global live events, media rights, and sponsorship monetization",
            "NXST": "NewsNation cable news, The CW Network & largest US operator of local TV broadcast stations",
            "TGNA": "Major local network affiliate TV stations (CBS/NBC/ABC/FOX), Locked On Podcast Network & Premion OTT ads",
            "GTN": "Top-rated local broadcast TV stations, regional sports channels & Assembly Studios production facilities",
            "VZ": "Nationwide 5G Ultra Wideband mobile network, Fios gigabit fiber broadband & enterprise connectivity",
            "T": "Nationwide 5G wireless network, AT&T Fiber multi-gigabit broadband & enterprise telecommunications",
            "TMUS": "Ultra Capacity 5G network leader, un-carrier wireless plans & 5G fixed wireless home internet",
            "CMCSA": "Xfinity multi-gigabit cable broadband internet, NBCUniversal, Peacock streaming & Xfinity Mobile",
            "CHTR": "Spectrum high-speed cable broadband, Spectrum Mobile converged wireless & enterprise fiber services"
        }
        competitors = []
        for idx, c in enumerate(selected_raw):
            t = c['ticker']
            offering = offerings_map.get(t, f"Leading offerings & market products in {industry}")
            competitors.append({
                "name": f"{c['company']} ({t})",
                "share": shares[idx] if idx < len(shares) else "5%",
                "key_offering": offering
            })

    return {
        "ticker": ticker_clean,
        "sector": sector,
        "industry": industry,
        "competitors": competitors
    }

def resolve_market_leaders(industry, market_segment):
    combined = f"{industry.lower()} {market_segment.lower()}"
    matched_slug = None

    sorted_slug_keys = sorted(FINVIZ_INDUSTRY_SLUGS.keys(), key=len, reverse=True)

    for key in sorted_slug_keys:
        if re.search(r'\b' + re.escape(key) + r'\b', combined):
            matched_slug = FINVIZ_INDUSTRY_SLUGS[key]
            break

    if not matched_slug:
        if re.search(r'\b(drug|pharma|health|biotech|medicine)\b', combined):
            matched_slug = "ind_drugmanufacturersgeneral,sec_healthcare"
        elif re.search(r'\b(auto|car|vehicle)\b', combined):
            matched_slug = "ind_automanufacturers,sec_consumercyclical"
        else:
            matched_slug = "ind_semiconductorequipmentmaterials,sec_technology"

    # Attempt live Finviz fetch
    live_companies = fetch_finviz_top_companies(matched_slug)
    
    if live_companies and len(live_companies) >= 3:
        shares = ["34%", "22%", "16%", "14%", "10%"]
        offerings_map = {
            "LLY": "Mounjaro / Zepbound GLP-1 receptor agonist therapies & oncology portfolio",
            "JNJ": "Oncology (Darzalex), Immunology (Stelara, Tremfya) & MedTech innovator",
            "ABBV": "Immunology (Skyrizi, Rinvoq, Humira) & Oncology (Imbruvica, Venclexta)",
            "MRK": "Keytruda immuno-oncology blockbuster, GARDASIL HPV vaccines & WINREVAIR",
            "NVS": "Entresto cardiovascular, Cosentyx immunology & Pluvicto radioligand therapies",
            "AZN": "Oncology (Tagrisso, Imfinzi) & Respiratory/Immunology biologics pipeline",
            "AMGN": "Oncology (Lumakras), Repatha cardiovascular & rare disease therapies",
            "GILD": "HIV antiviral treatments (Biktarvy), Oncology (Trodelvy) & Cell Therapies",
            "PFE": "Comirnaty mRNA vaccines, Paxlovid antivirals & Vyndaqel cardiovascular",
            "NVO": "Ozempic / Wegovy obesity & diabetes care franchises",
            "TSLA": "Full Self-Driving (FSD) neural net, Megapack energy, 4680 cells & EV market leader",
            "TM": "Global hybrid volume leader, Toyota Production System (TPS) & solid-state battery R&D",
            "GM": "Ultium EV architecture, Super Cruise hands-free driving & BrightDrop commercial fleet",
            "RACE": "Ultra-luxury high-margin sports cars, hybrid V8/V12 powertrains & brand equity",
            "F": "F-150 Lightning EV truck, Mustang Mach-E & Ford Pro commercial software",
            "ASML": "Monopolistic EUV (Extreme Ultraviolet) & High-NA lithography systems for sub-3nm nodes",
            "AMAT": "Broadest materials engineering, chemical/physical vapor deposition (CVD/PVD) & planarization",
            "LRCX": "Dominant high-aspect-ratio wafer etching and selective deposition for 3D NAND & logic",
            "KLAC": "World-leading process control, optical wafer inspection, metrology & yield management",
            "GD": "Gulfstream business jets, Virginia/Columbia-class nuclear submarines, & land combat vehicles",
            "RTX": "Patriot missile defense systems, Pratt & Whitney GTF engines, & NASAMS air defense",
            "LMT": "F-35 Lightning II joint strike fighter, HIMARS rocket artillery, & PAC-3 missile interceptors",
            "BA": "737/787 commercial jetliners, AH-64 Apache helicopters, & KC-46 aerial refuelers",
            "NOC": "B-21 Raider stealth bomber, Sentinel ICBM, & autonomous unmanned aerial systems (UAS)",
            "NFLX": "Pure-play subscription video-on-demand (SVOD) leader with global original content, ad-tier, & live streaming",
            "DIS": "Integrated media titan spanning ABC TV network, ESPN live sports, Disney+/Hulu streaming, Pixar/Marvel IP & Parks",
            "WBD": "Max streaming service, Warner Bros. film/TV studios, HBO premium cable, CNN news & TNT Sports",
            "LYV": "Global leader in live event promotion, venue operations, and Ticketmaster primary/secondary ticketing platform",
            "FOXA": "Fox News Media, Fox Sports live broadcasting, Fox broadcast network & Tubi free ad-supported streaming (FAST)",
            "FOX": "Fox News Channel, Fox Business, Fox Sports live events & Tubi streaming video platform",
            "PARA": "CBS Television Network, Paramount+ direct-to-consumer streaming, CBS News, Nickelodeon & MTV cable networks",
            "TKO": "UFC combat sports & WWE sports entertainment global live events, media rights, and sponsorship monetization",
            "NXST": "NewsNation cable news, The CW Network & largest US operator of local TV broadcast stations",
            "TGNA": "Major local network affiliate TV stations (CBS/NBC/ABC/FOX), Locked On Podcast Network & Premion OTT ads",
            "GTN": "Top-rated local broadcast TV stations, regional sports channels & Assembly Studios production facilities",
            "VZ": "Nationwide 5G Ultra Wideband mobile network, Fios gigabit fiber broadband & enterprise connectivity",
            "T": "Nationwide 5G wireless network, AT&T Fiber multi-gigabit broadband & enterprise telecommunications",
            "TMUS": "Ultra Capacity 5G network leader, un-carrier wireless plans & 5G fixed wireless home internet",
            "CMCSA": "Xfinity multi-gigabit cable broadband internet, NBCUniversal, Peacock streaming & Xfinity Mobile",
            "CHTR": "Spectrum high-speed cable broadband, Spectrum Mobile converged wireless & enterprise fiber services",
            "KO": "Global non-alcoholic concentrate model, sparkling soft drinks, hydration, and ready-to-drink coffee/tea",
            "PEP": "Integrated beverage & snack titan with direct-store-delivery (DSD) logistics and global brand scale",
            "MNST": "Dominant energy drink brand ecosystem leveraging Coca-Cola's global bottling distribution network",
            "KDP": "Leading single-serve coffee system (Keurig) integrated with iconic soft drinks & premium waters",
            "CELH": "High-growth functional essential energy drinks for fitness & thermogenic fat burn lifestyle consumers",
            "DEO": "World's leading premium spirits distiller operating iconic scotch, tequila, vodka, and gin global brand portfolios",
            "STZ": "Dominant importer of high-end Mexican beers, ultra-premium Napa wines, and craft spirits across North America",
            "BF-B": "Global American whiskey leader, premium tequila, and ready-to-drink (RTD) spirit cocktails",
            "PRNDY": "Global co-leader in wines & spirits specializing in prestige single malt scotch, cognac, and champagne",
            "NAPA": "Premier luxury Napa Valley wine producer specializing in estate Cabernet Sauvignon, Merlot, and Pinot Noir",
            "WMT": "Global retail superpower operating hypermarkets, Walmart+ subscription, advertising network, and high-efficiency logistics",
            "COST": "High-volume membership warehouse club delivering extreme unit value, Kirkland Signature brands, and high loyalty",
            "TGT": "Omnichannel discount retailer combining trendy designer partnerships with essential groceries and Drive Up fulfillment",
            "DG": "Rural discount general merchant delivering small-box neighborhood convenience and consumable goods across 19,000+ stores",
            "DLTR": "Fixed-price and multi-price point dollar store operator (Dollar Tree & Family Dollar) serving budget-conscious shoppers",
            "CTVA": "Pure-play agricultural innovator specializing in high-yield seed genetics, crop protection chemistry, and digital farming software",
            "ADM": "Global agricultural processing titan operating oilseed crushing, grain merchandising, and human/animal nutrition ingredients",
            "BG": "World leader in oilseed processing, grain sourcing, and sustainable plant-based oil manufacturing for food & bioenergy",
            "TSN": "Integrated protein producer operating processing, distribution, and branded chicken, beef, pork, and prepared foods",
            "DAR": "Global leader in converting edible and inedible bio-nutrients into sustainable bio-energy, renewable diesel, and specialty ingredients",
            "CALM": "Largest US producer & distributor of fresh shell eggs, specialty cage-free eggs, and liquid egg products",
            "AGRO": "South American agribusiness operator producing ethanol, sugar, rice, milk, and soybean commodities",
            "DOLE": "Global fresh produce leader producing and distributing fresh fruit, packaged salads, and pineapples/bananas",
            "VITL": "Pasture-raised egg and butter brand innovator delivering ethically produced pasture-raised dairy & shell eggs"
        }

        top_products_map = {
            "CTVA": ["Pioneer Brand Seed Corn & Soybeans", "Enlist Weed Control System & Chemistry", "Vorceed Enlist Corn Insect Protection Technology"],
            "ADM": ["Crude & Refined Vegetable Oils (Soybean, Canola)", "Biofuels & Industrial Ethanol Solutions", "Specialty Food & Animal Nutrition Ingredients"],
            "BG": ["Bulk Soybean & Oilseed Meal Processing", "Plant-Based Specialty Oils & Fats", "Sustainable Biofuel Feedstock Logistics"],
            "TSN": ["Tyson Fresh & Frozen Prepared Chicken", "Jimmy Dean Breakfast Meats & Sandwiches", "Hillshire Farm & Ball Park Brand Products"],
            "DAR": ["Diamond Green Diesel (DGD) Renewable Fuel", "Gelita Specialty Gelatin & Collagen Peptides", "Nature Safe Organic & Bio-Nutrient Fertilizers"],
            "CALM": ["Cal-Maine Fresh Grade A Shell Eggs", "Eggland's Best Specialty & Organic Eggs", "Farmhouse Eggs Pasture-Raised Series"],
            "AGRO": ["Adecoagro Sugarcane Ethanol & Bioelectricity", "Montelindo Processed Rice & Dairy Products", "Adecoagro High-Yield Soybean & Corn Crops"],
            "DOLE": ["Dole Fresh Premium Bananas & Pineapples", "Dole Chopped Salad Kits & Value Packs", "Dole Packaged Fruit & Fruit Bowls"],
            "VITL": ["Vital Farms Pasture-Raised Grade A Eggs", "Vital Farms Pasture-Raised Sea Salted Butter", "Vital Farms Liquid Whole Eggs & Whites"],
            "WMT": ["Great Value Private Label Grocery & Household Line", "Walmart+ Free Delivery & Shipping Membership", "Equate Health & Personal Care Brand Portfolio"],
            "COST": ["Kirkland Signature Premium Food & Household Line", "Costco Executive Membership & Cash-Back Rewards", "Costco Wholesale Grocery & Fuel Services"],
            "TGT": ["Good & Gather Grocery & Favorite Day Brands", "Threshold & Room Essentials Home Furnishings", "Target Circle Loyalty Program & Drive Up Pickup"],
            "DG": ["Clover Valley Grocery & Smart Way Budget Line", "DG Fresh Cold Supply Chain Consumables", "Dollar General $1 Value Merchandise Aisle"],
            "DLTR": ["Dollar Tree $1.25 & $3-$5 Plus Variety Items", "Family Dollar Consumables & Household Cleaners", "Crafter's Square & Seasonal Party Supplies"],
            "DEO": ["Johnnie Walker Scotch Whisky & Crown Royal", "Casamigos & Don Julio Premium Tequilas", "Tanqueray Gin, Smirnoff Vodka & Baileys"],
            "STZ": ["Modelo Especial & Corona Extra Beer Franchises", "Meiomi & The Prisoner Wine Company Portfolios", "High West Whiskey & Mi CAMPO Tequila"],
            "BF-B": ["Jack Daniel's Tennessee Whiskey (Old No. 7)", "Woodford Reserve Super-Premium Bourbon", "Herradura & el Jimador Tequilas"],
            "PRNDY": ["Jameson Irish Whiskey & Chivas Regal Scotch", "Martell Cognac & Glenlivet Single Malt", "Absolut Vodka & Perrier-Jouët Champagne"],
            "NAPA": ["Duckhorn Vineyards Napa Valley Cabernet", "Decoy Premium California Wine Series", "Kosta Browne & Goldeneye Pinot Noir"],
            "KO": ["Coca-Cola Trademark (Original, Zero Sugar, Diet)", "Sprite, Fanta & Fresca Sparkling Beverages", "Fairlife Ultra-Filtered Milk & BodyArmor Hydration"],
            "PEP": ["Pepsi-Cola Trademark (Pepsi Zero Sugar, Wild Cherry)", "Gatorade Thirst Quencher & Fast Twitch Energy", "Mountain Dew, Starry & Lipton RTD Teas"],
            "KO": ["Coca-Cola Trademark (Original, Zero Sugar, Diet)", "Sprite, Fanta & Fresca Sparkling Beverages", "Fairlife Ultra-Filtered Milk & BodyArmor Hydration"],
            "PEP": ["Pepsi-Cola Trademark (Pepsi Zero Sugar, Wild Cherry)", "Gatorade Thirst Quencher & Fast Twitch Energy", "Mountain Dew, Starry & Lipton RTD Teas"],
            "MNST": ["Monster Energy Original, Ultra & Rehab Lines", "Reign Total Body Fuel & Reign Storm Energy", "Bang Energy & Java Monster Coffee Drinks"],
            "KDP": ["Dr Pepper Trademark & Cream Soda Series", "Keurig Single-Serve Coffee Pods & Appliances", "Snapple, Core Hydration & Mott's Juices"],
            "CELH": ["Celsius Essential Energy Drinks (Sparkling / Green Tea)", "Celsius On-The-Go Powder Stick Packs", "Celsius Essentials High-Performance Energy Line"],
            "NFLX": ["Netflix Original Streaming Series & Movies", "Netflix Standard with Ads Membership Tier", "Netflix Live Sports & Global Entertainment Specials"],
            "DIS": ["ABC Broadcast Network & ESPN Live Sports", "Disney+ & Hulu Direct-to-Consumer Streaming", "Walt Disney Motion Picture Studios & Theme Parks"],
            "WBD": ["Max Direct-to-Consumer Streaming Platform", "CNN Worldwide News Network & Digital", "Warner Bros. Feature Films & HBO Originals"],
            "LYV": ["Ticketmaster Ticketing Platform", "Live Nation Concert Tours & Music Festivals", "Global Venue Management & Sponsorship Services"],
            "FOXA": ["Fox News Channel & FOX Business Network", "Fox Sports Live NFL, MLB & College Football", "Tubi Free Ad-Supported Streaming (FAST) Platform"],
            "FOX": ["Fox News Channel & FOX Business", "Fox Sports Live Broadcasting", "Tubi Streaming Video Platform"],
            "PARA": ["CBS Broadcast Network & CBS Sports", "Paramount+ Direct-to-Consumer Streaming", "Nickelodeon, MTV & Comedy Central Networks"],
            "TKO": ["UFC Live Pay-Per-View Events & Fight Pass", "WWE Raw, SmackDown & NXT Live Programming", "TKO Global Brand Partnerships & Licensing"],
            "NXST": ["NewsNation Cable News Network", "The CW Television Network", "Nexstar Local TV Stations & Digital Media"],
            "TGNA": ["Local NBC/CBS/ABC/FOX TV Station Affiliates", "Locked On Podcast Network", "Premion OTT Local Video Advertising"],
            "GTN": ["Gray Local Broadcast Station Portfolio", "Assembly Studios Media Production", "Local News Live Digital Stream Channel"],
            "VZ": ["Verizon 5G Mobility Voice & Data Plans", "Verizon Fios Gigabit Fiber Internet", "Verizon Business Managed Network Services"],
            "T": ["AT&T 5G Wireless Mobility Services", "AT&T Fiber Broadband Internet", "AT&T Dedicated Business Cloud Networking"],
            "TMUS": ["T-Mobile Go5G & Magenta Mobile Plans", "T-Mobile 5G Fixed Wireless Home Internet", "T-Mobile for Business 5G Enterprise Solutions"],
            "CMCSA": ["Xfinity Multi-Gigabit Cable Broadband", "NBCUniversal Broadcast & Peacock Streaming", "Xfinity Mobile Converged Wireless"],
            "CHTR": ["Spectrum Broadband Internet", "Spectrum Mobile Converged Wireless", "Spectrum Enterprise Managed Fiber Services"],
            "INTC": ["Core i9 / Ultra Client Processors", "Xeon Scalable Server CPUs", "Intel Foundry Services (IFS) Wafer Fabrication"],
            "AMD": ["EPYC Data Center Server Processors", "Ryzen AI Desktop & Mobile CPUs", "Instinct MI300X AI Accelerators"],
            "MU": ["High-Bandwidth Memory (HBM3E)", "DDR5 Server DRAM Modules", "UFS 4.0 / NVMe Flash Storage"],
            "TXN": ["Analog Signal Chain ICs", "C2000 Microcontrollers", "TPS Power Management Controllers"],
            "MRVL": ["Custom AI Compute ASICs", "PAM4 Optical DSP Interconnects", "OCTEON Data Center Storage Processors"],
            "NVDA": ["Blackwell / H100 Tensor Core GPUs", "CUDA Parallel Computing Software Stack", "Quantum-2 InfiniBand Networking"],
            "TSMC": ["N3 / N3E 3nm Advanced Node Foundry Wafers", "CoWoS Advanced 3D Packaging", "N4P 4nm HPC Semiconductor Processing"],
            "AVGO": ["Tomahawk 5 51.2Tbps Ethernet Switches", "Jericho3-AI Fabric Routers", "Custom AI ASIC Accelerator Engines"],
            "LLY": ["Mounjaro (Tirzepatide Injection)", "Zepbound (Obesity Treatment)", "Verzenio (Oncology Breast Cancer)"],
            "JNJ": ["Darzalex (Multiple Myeloma Biologic)", "Stelara (Plaque Psoriasis & IBD)", "Tremfya (IL-23 Inhibitor)"],
            "ABBV": ["Skyrizi (IL-23 Inhibitor)", "Rinvoq (JAK Inhibitor)", "Humira (TNF-Alpha Blocker)"],
            "MRK": ["Keytruda (Anti-PD-1 Immuno-Oncology)", "GARDASIL 9 (HPV Vaccine)", "WINREVAIR (Pulmonary Arterial Hypertension)"],
            "NVS": ["Entresto (Heart Failure Therapy)", "Cosentyx (Secukinumab Biologic)", "Pluvicto (Radioligand Therapy)"],
            "XOM": ["Permian Basin Low-Cost Unconventional Crude", "Guyana Offshore Deepwater Production", "Mobil 1 Synthetic Lubricants & Chemicals"],
            "CVX": ["Tengizchevroil Future Growth Project Crude", "Gulf of Mexico Deepwater Anchor Platform", "Chevron Renewable Clean Fuels"],
            "SHEL": ["Global LNG Integrated Trading & Shipping", "Deepwater Gulf of Mexico / Brazil Assets", "Shell Recharge EV Charging Network"],
            "TTE": ["Global Integrated LNG Export Supply", "Offshore Deepwater Upstream Oil", "TotalEnergies Renewable Solar & Wind Infrastructure"],
            "BP": ["Upstream Deepwater Oil & Gas Production", "Whiting & Cherry Point Refining Operations", "BP Pulse EV Rapid Charging Network"],
            "V": ["VisaNet Global Clearing & Authorization Network", "Visa Token Service (VTS) Security Infrastructure", "Visa Direct Real-Time P2P Payments"],
            "MA": ["Mastercard Integrated Processing Network", "Cyber & Intelligence Fraud Solutions", "Mastercard Open Banking & API Gateway"],
            "AXP": ["Centurion / Platinum Premium Credit Cards", "Merchant Closed-Loop Network Processing", "Amex Express Rewards & Travel Services"],
            "PYPL": ["Branded PayPal Digital Express Checkout", "Venmo Social Peer-to-Peer Wallet", "Braintree Merchant Payment Gateway"],
            "COF": ["Venture X & Spark Business Credit Cards", "Capital One 360 Digital Banking", "Capital One Auto Navigator Lending"],
            "TSLA": ["Model Y / Model 3 Electric Vehicles", "Full Self-Driving (FSD) Neural Network", "Megapack Commercial Energy Storage"],
            "TM": ["Toyota RAV4 & Prius Hybrid Powertrains", "Toyota Production System (TPS) Automotive Scale", "Lexus Luxury Electrified Vehicles"],
            "GM": ["Chevrolet Silverado & Equinox Ultium EVs", "Super Cruise Autonomous Highway Driving", "BrightDrop Commercial Electric Vans"],
            "RACE": ["Ferrari SF90 Stradale Hybrid Supercar", "Purosangue V12 High-Performance SUV", "296 GTB Plug-In Hybrid Sports Car"],
            "F": ["F-150 Lightning & Commercial Power Trucks", "Mustang Mach-E Electric Crossover", "Ford Pro Fleet Management Telematics"],
            "ASML": ["Twinscan EXE High-NA EUV Lithography", "Twinscan NXE 0.33 NA EUV Systems", "YieldStar Optical Metrology & Inspection"],
            "AMAT": ["Centura & Endura Thin Film PVD Systems", "Producer Chemical Vapor Deposition (CVD)", "VeritySEM Inline Metrology & Inspection"],
            "LRCX": ["Vector High-Aspect-Ratio Etch Systems", "ALTUS Tungsten / 3D NAND Deposition", "Kiyo Conductor Wafer Etching Platforms"],
            "KLAC": ["KLA 39xx Broadband Optical Inspection", "Voyager Wafer Defect Inspection Systems", "5D Analyzer Process Control Metrology"],
            "GD": ["Gulfstream G700 / G800 Business Jets", "Virginia & Columbia-Class Nuclear Submarines", "M1A2 SEPv3 Abrams Main Battle Tanks"],
            "RTX": ["Patriot MIM-104 Air & Missile Defense", "Pratt & Whitney GTF Aircraft Engines", "NASAMS Air Defense System"],
            "LMT": ["F-35 Lightning II Joint Strike Fighter", "M142 HIMARS Precision Rocket Artillery", "PAC-3 MSE Missile Interceptors"],
            "BA": ["737 MAX & 787 Dreamliner Commercial Jets", "AH-64E Apache Attack Helicopters", "KC-46A Pegasus Aerial Refuelers"],
            "NOC": ["B-21 Raider Stealth Strategic Bomber", "Sentinel LGM-35A ICBM System", "RQ-4 Global Hawk Autonomous UAS"]
        }
        
        providers = []
        for idx, comp in enumerate(live_companies[:5]):
            t = comp["ticker"]
            offering = offerings_map.get(t, f"Market-leading therapeutic & product offerings in {market_segment}")
            default_prods = [f"Flagship {market_segment} Product Line", f"Enterprise Solution for {t}", f"Next-Gen {industry} Platform"]
            top_prods = top_products_map.get(t, default_prods)
            share_val = shares[idx] if idx < len(shares) else "5%"
            providers.append({
                "name": f"{comp['company']} ({t})",
                "share": share_val,
                "key_offering": offering,
                "top_products": top_prods
            })
        return providers

    # Fallback to curated DB
    if matched_slug in CURATED_FINVIZ_DB:
        return CURATED_FINVIZ_DB[matched_slug]

    return [
        {"name": f"Apex {market_segment} Corp", "share": "36%", "key_offering": "Flagship market provider"},
        {"name": f"NexGen {industry} Inc", "share": "24%", "key_offering": "Automated enterprise platform"},
        {"name": f"Vanguard {market_segment} Tech", "share": "18%", "key_offering": "High-growth niche innovator"}
    ]

def build_structured_trends(industry, segment, providers):
    top_name = providers[0]['name'] if providers else "Industry Leaders"
    combined_text = f"{industry.lower()} {segment.lower()}"
    
    is_defense = any(k in combined_text for k in ["aerospace", "defense", "industrial", "industrials", "military", "weapon", "arms"])
    is_energy = any(k in combined_text for k in ["energy", "oil", "gas", "petroleum", "refining"]) and not is_defense
    is_pharma = any(k in combined_text for k in ["drug", "pharma", "health", "biotech", "medicine"]) and not is_energy and not is_defense
    is_auto = any(k in combined_text for k in ["auto", "automotive", "car", "vehicle"]) and not is_pharma and not is_energy and not is_defense
    is_financial = any(k in combined_text for k in ["financial", "credit", "banking", "payments", "card"]) and not is_energy and not is_pharma and not is_auto and not is_defense
    is_media = any(k in combined_text for k in ["communication", "media", "broadcasting", "entertainment", "tv", "television", "news", "shows", "streaming"]) and not is_financial and not is_auto and not is_pharma and not is_energy and not is_defense
    is_lodging = any(k in combined_text for k in ["lodging", "hotel", "hotels", "resort", "resorts", "hospitality"])
    is_home_improvement = any(k in combined_text for k in ["home improvement", "hardware", "diy", "renovation", "remodeling", "building supplies", "home depot", "lowe's", "lowes"])
    is_discount_stores = any(k in combined_text for k in ["discount store", "discount stores", "dollar store", "dollar stores", "supercenter", "supercenters", "warehouse club", "walmart", "costco", "target store", "dollar general", "dollar tree"])
    is_wineries = any(k in combined_text for k in ["winery", "wineries", "distillery", "distilleries", "wine", "spirits", "liquor", "tequila", "whiskey", "bourbon", "vodka", "cognac", "diageo", "jack daniel", "modelo"])
    is_beverages = any(k in combined_text for k in ["beverage", "beverages", "drink", "drinks", "soda", "coca-cola", "pepsi", "gatorade", "monster", "celsius"]) and not is_wineries
    is_retail = any(k in combined_text for k in ["retail", "department", "store", "apparel", "e-commerce", "luxury goods"]) and not is_home_improvement and not is_lodging and not is_auto and not is_media and not is_financial and not is_pharma and not is_energy and not is_defense and not is_beverages and not is_wineries and not is_discount_stores

    if is_discount_stores:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Accelerating consumer 'Trade-Down' behavior across all income brackets driving traffic to discount supercenters and warehouse clubs; expansion of high-margin private label consumables (Great Value, Kirkland Signature, Good & Gather); and growth of retail media ad networks (Walmart Connect). [nrf.com](https://nrf.com/research)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "The U.S. discount stores and supercenters market reached $1.28 trillion in 2025 and is projected to expand at a 4.6% CAGR to exceed $1.65 trillion by 2030, led by grocery supercenters (+5.8% CAGR) and warehouse membership clubs. [statista.com](https://www.statista.com/topics/1101/discount-stores-in-the-us/)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Shoppers prioritize non-discretionary grocery and household consumables over general merchandise, while expanding their usage of value-focused private label brands ($0.20–$0.40 savings per unit) to stretch household budgets. [mckinsey.com](https://www.mckinsey.com/industries/retail/our-insights)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Middle and upper-income households increasingly shop at Walmart and Costco for grocery savings; small-box dollar store footprint expands rapidly in underserved rural food deserts; and automated DC logistics reduce store stocking overhead. [census.gov](https://www.census.gov/retail)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Widespread consumer usage of mobile app barcode scanning, drive-thru curbside pickup (Target Drive Up / Walmart Pickup), and personalized digital loyalty app rewards (Target Circle, Walmart+). [statista.com](https://www.statista.com/topics/1101/discount-stores-in-the-us/)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Retail giants Walmart Inc. (42% market share) and Costco Wholesale (28% market share) command pricing power through supplier volume leverage, while Target (14%), Dollar General (10%), and Dollar Tree (6%) compete on proximity convenience and private label margins. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Retail theft and organized inventory shrink, store associate wage inflation, supply chain freight rate volatility, and margin compression when general merchandise discretionary spending cools. [nrf.com](https://nrf.com/research)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Discount store operators with automated supply chain scale, grocery market share dominance, and high-margin private label brand equity will capture long-term retail market share. [mckinsey.com](https://www.mckinsey.com/industries/retail/our-insights)"
            }
        }
    elif is_wineries:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Accelerating consumer 'Premiumization' (drinking less volume, but higher quality); surging demand for Super-Premium Tequila and Small-Batch Bourbon; rapid growth of canned spirit Ready-To-Drink (RTD) cocktails (Jack & Coke canned, High Noon); and expansion of direct-to-consumer (DTC) winery shipping. [statista.com](https://www.statista.com/topics/1758/spirits-and-wine/)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "The global wine and spirits market reached $920 billion in 2025 and is projected to reach $1.15 trillion by 2030 at a 5.2% CAGR, propelled by ultra-premium spirits (+8.6% CAGR) and RTD canned cocktails (+14.2% CAGR). [distilledspirits.org](https://www.distilledspirits.org/news/)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Consumers are trading up from commercial-tier spirits to premium Reposado/Añejo Tequila ($40–$100+/bottle) and single-malt scotch, while Gen Z & Millennials favor low-calorie RTD spirit cans and zero-alcohol botanical alternatives. [mckinsey.com](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Spirits have officially surpassed Beer in US market revenue share for the first time; Tequila/Mezcal sales growth is outstripping Vodka; and traditional distributor networks are adapting to rapid e-commerce on-demand delivery (Uber Eats / Drizly). [distilledspirits.org](https://www.distilledspirits.org/news/)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "High consumer reliance on e-commerce spirit delivery apps, barcode vintage scanner apps (Vivino), anti-counterfeiting RFID/NFC tags on luxury bottles, and digital winery tasting room booking portals. [statista.com](https://www.statista.com/topics/1758/spirits-and-wine/)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Global spirits titan Diageo plc (38% market share), Constellation Brands (28% market share), and Brown-Forman (16% market share) control exclusive wholesale distributor relationships (Three-Tier System), securing prime retail end-caps and bar well distribution. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Regulatory compliance with the US Three-Tier alcohol distribution system, climate change impacts on vineyard grape harvests and water availability, glass bottle packaging supply chain inflation, and international trade tariffs. [ttb.gov](https://www.ttb.gov/)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Wineries and distilleries focusing on ultra-premium agave/tequila expansion, master distiller oak barrel-aging programs, and high-margin canned RTD spirit cocktails will achieve superior operating margins. [mckinsey.com](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights)"
            }
        }
    elif is_beverages:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Rapid consumer migration away from high-sugar carbonated soft drinks toward zero-sugar, functional energy, electrolyte hydration, and ultra-filtered dairy/plant-based beverages; market size expanding toward $1.45 trillion globally; DSD (Direct-Store-Delivery) route efficiency and strategic bottling alliances (KO-MNST, PEP-CELH) dominating prime retail shelf space. [statista.com](https://www.statista.com/topics/1665/beverage-industry/)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "The global non-alcoholic beverage market reached $1.15 trillion in 2025 and is projected to expand at a 5.8% CAGR to exceed $1.45 trillion by 2030, propelled by functional energy (+12.4% CAGR) and premium hydration categories. [beverage-digest.com](https://www.beverage-digest.com/)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Consumers exhibit high willingness to pay premium price points ($2.50-$4.00 per unit) for functional health benefits (zero-sugar, natural caffeine, electrolytes, probiotics, protein) while spending on full-sugar carbonated soft drinks contracts. [mckinsey.com](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Structural pivot toward 'Better-For-You' (BFY) formulations, with zero-sugar lines (Coca-Cola Zero Sugar, Pepsi Zero Sugar, Monster Ultra, Celsius) outperforming legacy full-calorie sodas. Concurrently, functional waters and RTD coffee continue to cannibalize traditional fruit juices. [beverage-digest.com](https://www.beverage-digest.com/)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Rising consumer insistence on clean labels, natural non-caloric sweeteners (Stevia/Monkfruit), transparent electrolyte ratios, smart fountain dispenser tech (Freestyle), and direct-to-consumer auto-replenishment subscriptions. [statista.com](https://www.statista.com/topics/1665/beverage-industry/)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "The Coca-Cola Company (38% market share) and PepsiCo (32% market share) control direct-store-delivery (DSD) bottling networks and end-cap displays, driving distribution for fast-growing partners Monster Beverage (14% share) and Celsius (6% share). [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Aluminum container & rPET resin packaging cost inflation, municipal sugar tax regulations in key global jurisdictions, water resource sustainability scrutiny, and aggressive retail supermarket slotting fee friction. [nrf.com](https://nrf.com/research)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Non-alcoholic beverage leaders with dominant DSD route-to-market scale and aggressive zero-sugar/functional energy innovation will capture the highest margin growth. [mckinsey.com](https://www.mckinsey.com/industries/consumer-packaged-goods/our-insights)"
            }
        }
    elif is_home_improvement:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Spending is forecast to shrink for the first time since 2010, with a shift toward essential repairs and minor upgrades; market size is projected to reach ~$1.29 trillion by 2035 at a 4.5% CAGR; technology adoption (AR/VR, smart home devices) is growing; and major retailers like Home Depot and Lowe’s dominate, with private label brands gaining share in tools and garden supplies. [accio.com](https://www.accio.com/business/home-improvement-retail-industry-trends)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "The U.S. home improvement market was valued at $828.8 billion in 2025 and is expected to reach $862.4 billion in 2026, with projections of $1.29 trillion by 2035 at a 4.5% CAGR. [accio.com](https://www.accio.com/business/home-improvement-retail-industry-trends)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Homeowners are prioritizing non-discretionary maintenance (roofing, HVAC, electrical, plumbing) and minor upgrades over high-ticket kitchen and bathroom remodels due to high mortgage rates and interest costs. [statista.com](https://www.statista.com/topics/1733/home-improvement-in-the-us/)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Over 86% of homeowners report deferring major renovations. Concurrently, an aging U.S. housing stock (over 40 years old on average) is driving sustained baseline demand for repair and maintenance hardware. [nrf.com](https://nrf.com/research)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Consumer adoption of spatial computing, AR room visualizers, and smart home IoT devices is expanding, alongside expectations for instant mobile store inventory lookup and BOPIS fulfillment. [accio.com](https://www.accio.com/business/home-improvement-retail-industry-trends)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "The Home Depot (28% market share) and Lowe's Companies (17% market share) command big-box market share, expanding Pro contractor loyalty platforms while proprietary private label tool brands (Husky, Kobalt, Craftsman) gain margin share. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Elevated mortgage interest rates suppressing existing home sales, volatility in lumber and building material supply chains, and ongoing trade contractor labor shortages. [census.gov](https://www.census.gov/construction/c30/c30index.html)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "While overall discretionary spending tightens, aging housing infrastructure guarantees persistent essential repair demand. Retailers leveraging Pro contractor integration and high-margin private labels will outperform. [mckinsey.com](https://www.mckinsey.com/industries/retail/our-insights)"
            }
        }
    elif is_lodging:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Rapid deployment of AI booking agents and dynamic pricing engines; market bifurcation favoring luxury and lifestyle hotel brands over economy chains; and guest preference shifting toward purpose-driven travel ('Whycations') and wellness retreats. [ahla.com](https://www.ahla.com/research)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "Global lodging and hotel market size reached $1.08 trillion in 2025 and is projected to expand at a 6.2% CAGR through 2032, driven by international travel resurgence and mega-event tourism. [statista.com](https://www.statista.com/topics/1102/hotels/)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "High-income travelers drive premium RevPAR growth across luxury and upper-upscale resorts, while price-sensitive consumer segments trade down to select-service properties or flexible extended-stay accommodations. [mckinsey.com](https://www.mckinsey.com/industries/travel-logistics-and-infrastructure)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Hotel operators are pivoting from top-line RevPAR focus to Net Operating Income (NOI) optimization via asset-light franchise expansion, automated check-in kiosks, and energy efficiency systems. [ahla.com](https://www.ahla.com/research)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Widespread consumer expectation for keyless smartphone room entry (<500ms response), generative AI concierge chat, and integrated mobile loyalty redemption (Marriott Bonvoy, Hilton Honors). [statista.com](https://www.statista.com/topics/1102/hotels/)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Asset-light hotel franchisors Marriott International (36% market share), Hilton Worldwide (28% market share), and Hyatt Hotels (18% market share) dominate direct bookings, capturing high-margin recurring fee streams. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Rising hospitality labor costs, hotel housekeeping staffing shortages, debt refinancing costs for commercial real estate owners, and OTA (Online Travel Agency) commission compression. [ahla.com](https://www.ahla.com/research)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Lodging industry growth is driven by direct digital guest engagement and luxury tier premiumization. Scale operators with dominant loyalty networks and asset-light franchise models capture the highest profit margins. [mckinsey.com](https://www.mckinsey.com/industries/travel-logistics-and-infrastructure)"
            }
        }
    elif is_retail:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Omnichannel integration blending physical department stores with direct-to-consumer mobile apps; rapid expansion of off-price apparel and luxury treasure-hunt retail; and AI-driven hyper-personalized marketing. [nrf.com](https://nrf.com/research)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "The U.S. department store and retail apparel market is valued at ~$740 billion in 2025, growing at a 3.8% CAGR with digital e-commerce channels capturing over 32% of total retail sales. [census.gov](https://www.census.gov/retail)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Consumers are exhibiting value-seeking behavior, driving outperformance in off-price retail (TJX Companies) and private-label fashion brands while selectively splurging on beauty and footwear. [statista.com](https://www.statista.com/topics/1097/department-stores/)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Retailers are shrinking traditional mall anchor store footprints in favor of off-mall, smaller experiential store formats and streamlined Buy-Online-Pickup-In-Store (BOPIS) fulfillment centers. [nrf.com](https://nrf.com/research)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Surge in mobile app shopping, friction-free RFID self-checkout, automated return kiosks, and AI-powered personalized style recommendations driving higher average basket values. [statista.com](https://www.statista.com/topics/1097/department-stores/)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "The TJX Companies (38% market share), Macy's Inc (24% market share), and Kohl's Corporation (16% market share) dominate store footprints, leveraging shop-in-shops (Sephora at Kohl's) to drive foot traffic. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Organized retail crime and inventory shrink, high promotional markdown pressures, supply chain lead-time volatility, and shifting consumer discretionary allocations. [nrf.com](https://nrf.com/research)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Retail success hinges on seamless omnichannel execution, agile supply chains, and off-price value positioning that captures budget-conscious fashion shoppers. [mckinsey.com](https://www.mckinsey.com/industries/retail/our-insights)"
            }
        }
    elif is_auto:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Accelerating transition toward Software-Defined Vehicles (SDVs), Level 2+/Level 3 autonomous highway driving, 800V ultra-fast EV charging architectures, and hybrid powertrain expansion. [iea.org](https://www.iea.org/reports/global-ev-outlook-2024)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "Global automotive industry revenue reached $2.85 trillion in 2025, with electric and hybrid vehicles projected to achieve a 18.5% CAGR through 2030, exceeding 45% of total global new car sales. [bloombergNEF](https://about.bnef.com/)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Automotive buyers prioritize Total Cost of Ownership (TCO), financing incentives, and battery warranty longevity while luxury automotive buyers show strong willingness to pay for premium autonomy and software packages. [statista.com](https://www.statista.com/topics/1020/automotive-industry/)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Automakers are shifting from pure ICE manufacturing toward modular EV platforms, unibody die-casting (Gigacasting), and internal battery chemistry development to lower assembly costs. [iea.org](https://www.iea.org/reports/global-ev-outlook-2024)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "High consumer demand for Over-The-Air (OTA) software feature updates, phone-as-a-key digital connectivity, and integrated high-resolution infotainment displays. [statista.com](https://www.statista.com/topics/1020/automotive-industry/)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Tesla Inc (38% EV market share), Toyota Motor (24% global hybrid leader), and General Motors (15% market share) lead competitive production, balancing EV scale against high-margin legacy ICE and hybrid light trucks. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Public EV fast-charging reliability, battery raw material (lithium/nickel) supply chain geopolitical risks, and high vehicle financing interest rates constraining mass-market affordability. [nhtsa.gov](https://www.nhtsa.gov/)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Automotive profitability requires balancing hybrid volume cash flows with aggressive SDV software and EV battery scale to maintain long-term competitive moats. [mckinsey.com](https://www.mckinsey.com/industries/automotive-and-assembly/our-insights)"
            }
        }
    elif is_defense:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Rapid proliferation of Unmanned Aerial Systems (UAS/Drones), electronic warfare (EW) counter-drone defense, precision munition replenishment, and JADC2 multi-domain battle networks. [sipri.org](https://www.sipri.org/research/armaments-and-disarmament)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "Global defense and aerospace expenditures expanded to $2.44 trillion in 2025, with allied NATO and Indo-Pacific procurement budgets growing at a 7.5% CAGR to recapitalize strategic deterrence assets. [defense.gov](https://www.defense.gov/News/Releases/)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Government procurement is shifting toward high-volume low-cost autonomous loitering munitions, missile interceptors (Patriot PAC-3, HIMARS), nuclear submarine modernization, and cyber-hardened satellite constellations. [mckinsey.com](https://www.mckinsey.com/industries/aerospace-and-defense)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Pivoting from counter-insurgency warfare to high-intensity peer conflict readiness, requiring defense prime contractors to scale manufacturing production output rapidly under multi-year contracts. [defense.gov](https://www.defense.gov/News/Releases/)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Defense customer requirements emphasize GPS-denied autonomous navigation, AI threat classification, open-architecture avionics, and modular mission system payloads. [sipri.org](https://www.sipri.org/research/armaments-and-disarmament)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Prime contractors General Dynamics (28% share), RTX Corporation (24% share), and Lockheed Martin (22% share) command long-term government programs of record and sole-source defense franchises. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Aerospace supply chain bottlenecks, specialized defense engineering workforce shortages, DFARS/CMMC 2.0 cybersecurity compliance mandates, and fixed-price contract margin compression. [defense.gov](https://www.defense.gov/News/Releases/)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Defense leaders with combat-proven weapons systems, resilient surge manufacturing capacity, and advanced software/autonomous capabilities hold decisive market advantages. [mckinsey.com](https://www.mckinsey.com/industries/aerospace-and-defense)"
            }
        }
    elif is_energy:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Geopolitical supply security focus, global LNG liquefaction infrastructure expansion, low-breakeven Permian Basin manufacturing scale, and carbon capture & storage (CCS) deployment. [eia.gov](https://www.eia.gov/outlooks/steo/)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "Global energy and oil & gas market revenues surpassed $4.2 trillion in 2025, with LNG export trading growing at a 8.4% CAGR to meet European and Asian energy security demand. [iea.org](https://www.iea.org/reports/world-energy-outlook-2024)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Supermajors maintain strict capital discipline, capping upstream exploration capex to fund record shareholder dividends/buybacks while selectively investing in high-margin deepwater assets. [opec.org](https://www.opec.org/opec_web/en/publications/338.htm)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Dual-track energy transition strategy balancing near-term crude oil production with multi-billion dollar commitments to hydrogen, bioenergy, and industrial carbon capture scale. [eia.gov](https://www.eia.gov/outlooks/steo/)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Commercial energy buyers demand guaranteed supply contract security, low-sulfur refined fuels (IMO 2020), and real-time carbon intensity reporting across midstream supply chains. [iea.org](https://www.iea.org/reports/world-energy-outlook-2024)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Integrated majors ExxonMobil (36% market share), Chevron (28% market share), and Shell plc (16% market share) dominate global crude production, refining, and LNG trading desks. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Crude price volatility, maritime chokepoint transit risks, EPA methane emission penalties, and stringent ESG capital constraints on long-cycle upstream projects. [eia.gov](https://www.eia.gov/outlooks/steo/)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Low-cost extraction breakevens (sub-$35/bbl Permian/Guyana) combined with integrated global LNG trading networks generate superior cash flow resilience across commodity price cycles. [mckinsey.com](https://www.mckinsey.com/industries/oil-and-gas/our-insights)"
            }
        }
    elif is_pharma:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Explosive demand for GLP-1 receptor agonist metabolic therapies (obesity/diabetes), targeted immuno-oncology blockbusters, antibody-drug conjugates (ADCs), and AI drug discovery. [fda.gov](https://www.fda.gov/drugs)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "Global pharmaceutical market valuation reached $1.58 trillion in 2025 and is projected to expand at a 6.8% CAGR through 2030, propelled by metabolic and oncology biotherapeutics. [iqvia.com](https://www.iqvia.com/insights)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Healthcare payers and patients prioritize high-efficacy specialty biopharmaceuticals with proven overall survival benefits, driving massive R&D reinvestment ($10B+ per market leader). [statista.com](https://www.statista.com/topics/1719/pharmaceutical-industry/)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Accelerated shift from traditional small-molecule oral pills to complex sterile biologics, subcutaneous auto-injectors, and radioligand precision oncology therapies. [fda.gov](https://www.fda.gov/drugs)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Patients and healthcare providers demand convenient once-weekly subcutaneous dosing, digital patient support platforms, and clear insurance reimbursement authorization. [iqvia.com](https://www.iqvia.com/insights)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Pharmaceutical titans Eli Lilly (34% market share), Johnson & Johnson (22% market share), and AbbVie (16% market share) lead commercial distribution via strong patent portfolios. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Patent cliff expirations, IRA Medicare price negotiations, FDA clinical trial approval hurdles, and complex cold-chain biologics manufacturing logistics. [fda.gov](https://www.fda.gov/drugs)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Pharma leadership requires category-defining therapeutic efficacy, deep clinical trial pipelines, and robust IP protection to withstand biosimilar competition. [mckinsey.com](https://www.mckinsey.com/industries/life-sciences/our-insights)"
            }
        }
    elif is_financial:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Universal adoption of contactless NFC payments, tokenized mobile digital wallets (Apple Pay/Google Wallet), real-time AI fraud mitigation, and Open Banking APIs. [federalreserve.gov](https://www.federalreserve.gov/paymentsystems.htm)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "Global credit services and payment processing transactions volume reached $14.5 trillion in 2025, growing at a 9.2% CAGR as cash transactions decline worldwide. [nilsonreport.com](https://nilsonreport.com/)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Consumers prefer premium reward credit cards, cash-back loyalty incentives, and Buy Now Pay Later (BNPL) installment options for online e-commerce transactions. [bis.org](https://www.bis.org/publ/arpdf2024e.htm)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Transition from legacy magnetic-stripe and paper check clearing to instant account-to-account (A2A) clearing networks (FedNow, RTP) and cross-border multi-currency settlement. [federalreserve.gov](https://www.federalreserve.gov/paymentsystems.htm)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Sub-second checkout expectation, biometric payment authentication, zero-liability fraud protection, and instant push notification transaction alerts. [nilsonreport.com](https://nilsonreport.com/)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Payment networks Visa Inc (38% market share), Mastercard (32% market share), and American Express (14% market share) capture dominant global merchant processing volumes. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "Evolving interchange fee cap regulations, sophisticated cyber-attacks and card-not-present fraud, and strict PCI-DSS v4.0 data security mandates. [federalreserve.gov](https://www.federalreserve.gov/paymentsystems.htm)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Two-sided network scale, sub-100ms authorization latencies, and AI-powered tokenized fraud prevention form invincible moats for market leaders. [mckinsey.com](https://www.mckinsey.com/industries/financial-services/our-insights)"
            }
        }
    elif is_media:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": "Key 2026 trends: Secular shift from linear cable TV to direct-to-consumer DTC streaming (SVOD/AVOD) and FAST channels; soaring live sports broadcasting rights valuations; and AI content curation. [nielsen.com](https://www.nielsen.com/insights/)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": "Global media and entertainment market size reached $2.55 trillion in 2025, growing at a 5.6% CAGR with streaming video and live sports rights driving top-line growth. [fcc.gov](https://www.fcc.gov/media)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": "Advertisers shift budgets into dynamic digital AVOD/FAST ad insertion while consumers stack low-cost ad-supported streaming subscriptions and live event tickets. [statista.com](https://www.statista.com/topics/995/media-in-the-us/)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": "Linear cable cord-cutting accelerating while media networks form strategic joint-venture streaming bundles and secure marquee live sports rights (NFL, NBA). [nielsen.com](https://www.nielsen.com/insights/)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": "Viewers demand sub-second 4K HDR video playback, personalized AI recommendations, and multi-screen mobile and smart TV app synchronization. [fcc.gov](https://www.fcc.gov/media)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": "Media giants Walt Disney (35% market share), Netflix (28% market share), and Warner Bros. Discovery (18% market share) dominate global subscriber scale and IP franchises. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": "High content production expenses, subscriber churn management, password-sharing controls enforcement, and declining linear carriage fee revenues. [fcc.gov](https://www.fcc.gov/media)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": "Scale operators combining premium IP, live sports, and efficient ad-tier monetization will capture profitable DTC streaming margins. [mckinsey.com](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights)"
            }
        }
    else:
        return {
            "trends": {
                "title": "Trends",
                "icon": "📈",
                "text": f"Key 2026 trends across {segment}: Accelerated capital expenditure into automated AI workflows, supply chain localization, and high-precision quality management. [statista.com](https://www.statista.com/)"
            },
            "market_size_growth": {
                "title": "Market Size and Growth",
                "icon": "📊",
                "text": f"The global {segment} market within {industry} was valued at ~$650 billion in 2025 and is projected to expand at a 6.5% CAGR through 2030. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "spending_patterns": {
                "title": "Spending Patterns",
                "icon": "💳",
                "text": f"Enterprise and retail clients in {segment} are prioritizing operational efficiency, pay-as-you-scale commercial terms, and energy-efficient product lines. [mckinsey.com](https://www.mckinsey.com/industries)"
            },
            "shifts_changes": {
                "title": "Shifts or Changes",
                "icon": "🔄",
                "text": f"Structural consolidation across major market providers in {segment}, driving strategic M&A to secure specialized intellectual property and customer reach. [statista.com](https://www.statista.com/)"
            },
            "tech_consumer_behavior": {
                "title": "Technology and Consumer Behavior",
                "icon": "🤖",
                "text": f"High demand for cloud API connectivity, automated self-monitoring architectures, and instant mobile service access across {segment} products. [gartner.com](https://www.gartner.com/en/research)"
            },
            "retail_competitive_landscape": {
                "title": "Retail and Competitive Landscape",
                "icon": "🏬",
                "text": f"Market leaders including {top_name} command high market share, establishing high customer switching costs and deep ecosystem integration moats. [bloomberg.com](https://www.bloomberg.com/markets)"
            },
            "challenges": {
                "title": "Challenges",
                "icon": "⚠️",
                "text": f"Macroeconomic inflation pressures, skilled technical labor availability, regulatory compliance costs, and raw material supply chain disruptions. [statista.com](https://www.statista.com/)"
            },
            "bottom_line": {
                "title": "Bottom Line",
                "icon": "🎯",
                "text": f"Organizations in {segment} that combine product innovation, strong customer lock-in, and operational cost discipline will sustain long-term market leadership. [mckinsey.com](https://www.mckinsey.com/industries)"
            }
        }

def generate_market_data(industry, market_segment, custom_providers=None):
    industry_clean = industry.strip()
    segment_clean = market_segment.strip()
    cache_key = f"{industry_clean.lower()}:{segment_clean.lower()}"

    if not custom_providers and cache_key in analysis_cache:
        return analysis_cache[cache_key]

    providers = custom_providers if custom_providers else resolve_market_leaders(industry_clean, segment_clean)


    seed_val = sum(ord(c) for c in cache_key)
    rng = random.Random(seed_val)

    top_3_providers = providers[:3]
    top_names_str = ", ".join([p["name"] for p in top_3_providers])

    base_market_size = rng.randint(150, 950)
    market_size_str = f"${base_market_size:.1f} Billion"
    growth_rate = rng.randint(10, 28)

    combined_text = f"{industry_clean.lower()} {segment_clean.lower()}"
    is_defense = any(k in combined_text for k in ["aerospace", "defense", "industrial", "industrials", "military", "weapon", "arms"])
    is_energy = any(k in combined_text for k in ["energy", "oil", "gas", "petroleum", "refining"]) and not is_defense
    is_pharma = any(k in combined_text for k in ["drug", "pharma", "health", "biotech", "medicine"]) and not is_energy and not is_defense
    is_auto = any(k in combined_text for k in ["auto", "automotive", "car", "vehicle"]) and not is_pharma and not is_energy and not is_defense
    is_financial = any(k in combined_text for k in ["financial", "credit", "banking", "payments", "card"]) and not is_energy and not is_pharma and not is_auto and not is_defense
    is_media = any(k in combined_text for k in ["communication", "media", "broadcasting", "entertainment", "tv", "television", "news", "shows", "streaming"]) and not is_financial and not is_auto and not is_pharma and not is_energy and not is_defense
    is_lodging = any(k in combined_text for k in ["lodging", "hotel", "hotels", "resort", "resorts", "hospitality"])
    is_home_improvement = any(k in combined_text for k in ["home improvement", "hardware", "diy", "renovation", "remodeling", "building supplies", "home depot", "lowe's", "lowes"])
    is_discount_stores = any(k in combined_text for k in ["discount store", "discount stores", "dollar store", "dollar stores", "supercenter", "supercenters", "warehouse club", "walmart", "costco", "target store", "dollar general", "dollar tree"])
    is_wineries = any(k in combined_text for k in ["winery", "wineries", "distillery", "distilleries", "wine", "spirits", "liquor", "tequila", "whiskey", "bourbon", "vodka", "cognac", "diageo", "jack daniel", "modelo"])
    is_beverages = any(k in combined_text for k in ["beverage", "beverages", "drink", "drinks", "soda", "coca-cola", "pepsi", "gatorade", "monster", "celsius"]) and not is_wineries
    is_farm_products = any(k in combined_text for k in ["farm product", "farm products", "agriculture", "agricultural", "agribusiness", "crop", "grain", "seed", "oilseed", "corteva", "adm", "archer-daniels", "bunge", "tyson", "darling ingredients"])
    is_retail = any(k in combined_text for k in ["retail", "department", "store", "apparel", "e-commerce", "luxury goods"]) and not is_home_improvement and not is_lodging and not is_auto and not is_media and not is_financial and not is_pharma and not is_energy and not is_defense and not is_beverages and not is_wineries and not is_discount_stores and not is_farm_products

    if is_farm_products:
        trends_list = [
            "Market Scale & Steady Defense Growth: Agribusiness market valued at ~$3.5 Trillion (targeting $4.5T by 2034 at 2.66% CAGR) with steady cash flow, inelastic demand, and inflation hedge stability",
            "AI as 'Connective Layer': AI coordinator platforms aggregating weather patterns, satellite crop health, soil sensors, and logistics into unified farm operating dashboards",
            "Biological Inputs & Climate Resilience: Rapid shift to bio-based crop protection, bio-fertilizers, and heat/drought-tolerant seed genetics reducing chemical environmental footprints",
            "Precision Agriculture & Traceability: Widespread adoption of variable-rate fertilizer applicators, autonomous harvesting robotics, and farm-to-shelf digital supply chain tracking"
        ]
        cust_pref_list = [
            "Proven yield drag protection against extreme weather anomalies (heat/drought) and pest resistance",
            "Biological crop nutrition and non-chemical pest management reducing environmental residues and regulatory friction",
            "Transparent farm-to-shelf traceability data and non-GMO / organic certification for global food buyers",
            "Reliable bulk commodity origination, low-friction equipment financing/leasing, and transparent crop futures pricing"
        ]
        exciting_list = [
            f"{providers[0]['name']} Pioneer seed germplasm, Enlist weed control system, & biological crop protection technology",
            f"{providers[1]['name']} global oilseed processing network, agricultural commodity merchandising, & nutrition ingredients",
            f"{providers[2]['name']} plant-based oilseed processing scale, sustainable bio-energy feedstocks, & specialty plant fats"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} integrated protein processing scale, Jimmy Dean & Hillshire Farm brand portfolio")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} Diamond Green Diesel renewable fuel joint-venture & bio-nutrient circular economy model")

        diff_list = [
            "Proprietary seed germplasm libraries and multi-decade agricultural biotech patent protection",
            "Global grain origination, port terminal, and oilseed processing asset footprint providing unmatched supply chain efficiency",
            "Deep relationships with commercial farm operators and comprehensive digital agronomy advisory platforms",
            "Leading circular economy conversion capacity transforming agricultural bio-nutrients into renewable energy and specialty products"
        ]
        comp_data = {
            "government": [
                "US USDA Animal and Plant Health Inspection Service (APHIS) Biotechnology Regulations",
                "US EPA Federal Insecticide, Fungicide, and Rodenticide Act (FIFRA) Pesticide Registration",
                "EU EFSA Genetically Modified Food & Feed Regulations & Deforestation Compliance (EUDR)"
            ],
            "industry": [
                "ASTA (American Seed Trade Association) Quality & Germination Testing Standards",
                "NGFA (National Grain and Feed Association) Trade Rules & Arbitration Standards",
                "ISCC (International Sustainability & Carbon Certification) for Biofuels & Biomass"
            ],
            "segment": [
                "Seed purity and germination rate tolerances (≥95% genetic purity, ≥90% germination rate)",
                "Grain moisture content (<13.5% for corn/soybeans) and aflatoxin toxin limits (<20 ppb)",
                "Crude vegetable oil free fatty acid (FFA) specs (<0.10%) and heavy metal purity testing"
            ]
        }
    elif is_discount_stores:
        trends_list = [
            "Accelerating consumer 'Trade-Down' behavior across all income brackets amid inflation, driving higher-income household foot traffic into discount supercenters",
            "Rapid expansion of high-margin private-label consumable brands (Great Value, Kirkland Signature, Good & Gather) capturing market share from national brands",
            "Growth of high-margin retail media advertising networks (Walmart Connect) utilizing first-party point-of-sale customer purchase data",
            "Aggressive deployment of automated distribution centers and micro-fulfillment hubs to lower store stocking costs and speed curbside delivery"
        ]
        cust_pref_list = [
            "Everyday Low Price (EDLP) pricing guarantees on essential food, beverage, paper goods, and personal care consumables",
            "High-quality private label alternatives offering 20-30% cost savings without sacrificing product performance or taste",
            "Frictionless curbside Drive-Up / BOPIS fulfillment with sub-2 hour order readiness and zero pickup fees",
            "Small-box neighborhood store proximity for rapid fill-in trips or high-volume warehouse bulk purchasing"
        ]
        exciting_list = [
            f"{providers[0]['name']} global hypermarket scale, Great Value grocery line, Walmart+ subscription, & Walmart Connect ad network",
            f"{providers[1]['name']} Kirkland Signature high-margin brand equity, Executive membership cash-back, & warehouse club unit value",
            f"{providers[2]['name']} Good & Gather grocery brands, Threshold home decor, Target Circle loyalty, & Drive Up curbside pickup"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} Clover Valley food line, DG Fresh cold supply chain, & 19,000+ rural neighborhood stores")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} Dollar Tree $1.25 & $3-$5 Plus multi-price merchandise & Family Dollar consumable goods")

        diff_list = [
            "Unrivaled supplier volume buying leverage and supply chain automation delivering lowest cost-per-unit retail distribution",
            "Massive physical store footprint providing strategic last-mile store fulfillment and BOPIS / curbside pickup hubs within 10 miles of 90% of US households",
            "Deep consumer trust and multi-billion-dollar private label brand equity (Kirkland Signature, Great Value)",
            "Proprietary first-party shopper data platforms driving targeted digital loyalty promotions and high-margin retail ad revenue"
        ]
        comp_data = {
            "government": [
                "US FTC Consumer Protection & Price Accuracy Regulations",
                "US USDA SNAP / EBT Food Stamp Payment Processing & WIC Program Compliance",
                "US OSHA Retail Warehouse Safety & Material Handling Operational Standards"
            ],
            "industry": [
                "NRF (National Retail Federation) Omnichannel & Data Exchange Standards",
                "PCI-DSS v4.0 Store POS Payment Terminal Security Compliance",
                "ISO 9001 Supply Chain Quality Systems & Food Safety HACCP Protocols"
            ],
            "segment": [
                "Real-time store inventory synchronization accuracy (>99.5%) across store POS & digital channels",
                "Curbside Drive-Up & BOPIS order fulfillment SLA (<2 hours from online placement)",
                "99.99% system uptime for SNAP / EBT electronic benefit transfer transaction processing"
            ]
        }
    elif is_wineries:
        trends_list = [
            "Accelerating consumer 'Premiumization' (drinking less volume, but higher quality) driving record sales in Super-Premium Tequila and Small-Batch Bourbon",
            "Rapid surge in spirit-based canned Ready-To-Drink (RTD) cocktails (Jack & Coke canned, High Noon) capturing market share from traditional malt beverages",
            "Spirits officially surpassing Beer in total US market revenue share, propelled by agave-based spirits (Tequila/Mezcal) outstripping Vodka",
            "Expansion of direct-to-consumer (DTC) winery subscription shipping and digital tasting room reservation ecosystems"
        ]
        cust_pref_list = [
            "Authentic craft heritage, master distiller oak-barrel aging, and single-estate Napa Valley terroir grape sourcing",
            "Premium taste profiles in agave spirits (Añejo / Reposado), super-premium bourbon, and single-malt scotch",
            "Convenient low-calorie spirit canned RTD cocktails and zero-sugar botanical alternatives",
            "Prestige packaging aesthetics, collectible bottle designs, and anti-counterfeit RFID authentication"
        ]
        exciting_list = [
            f"{providers[0]['name']} global spirits leader, Johnnie Walker scotch, Casamigos & Don Julio tequilas, & Baileys cream",
            f"{providers[1]['name']} Modelo Especial & Corona beer dominance, Meiomi & The Prisoner Napa wine portfolios, & High West whiskey",
            f"{providers[2]['name']} Jack Daniel's Tennessee Whiskey (Old No. 7), Woodford Reserve bourbon, & Herradura tequila"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} Jameson Irish whiskey, Martell cognac, Glenlivet single malt, & Absolut vodka")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} Duckhorn Vineyards Napa Cabernet, Decoy Series, & Kosta Browne Pinot Noir")

        diff_list = [
            "Exclusive Three-Tier distributor allocation networks providing prime bar well and retail end-cap placement",
            "Multi-decade oak barrel aging inventories and proprietary master distiller formulation secrets",
            "Agave farming scale and prime Napa Valley / Sonoma Valley estate vineyard real estate holdings",
            "Massive global brand equity driving high pricing power and resilience across economic cycles"
        ]
        comp_data = {
            "government": [
                "US TTB (Alcohol & Tobacco Tax & Trade Bureau) COLA Label Approval & DSP Distillation Permits",
                "US State ABC (Alcoholic Beverage Control) Three-Tier System & Mandatory Wholesaler Licensing Laws",
                "EU Geographical Indication (GI) Laws & Mexican Tequila Regulatory Council (CRT) NOM Regulations"
            ],
            "industry": [
                "DISCUS (Distilled Spirits Council of the US) Code of Responsible Practices for Beverage Alcohol",
                "Wine Institute Sustainable Winegrowing Environmental & Water Management Standards",
                "ISO 9001 Quality Management Systems for High-Speed Spirits & Wine Bottling Plants"
            ],
            "segment": [
                "Proof / Alcohol-by-Volume (ABV) hydrometer precision testing (±0.2% ABV) and tax determination compliance",
                "Oak barrel rickhouse temperature & humidity warehouse specifications for optimal whiskey maturation",
                "Wine bottling sulfur dioxide (SO2) stability testing, dissolved oxygen control, and sterile filtration specs"
            ]
        }
    elif is_beverages:
        trends_list = [
            "Rapid consumer shift from high-sugar soft drinks to zero-sugar, functional energy, electrolyte hydration, and ultra-filtered protein beverages",
            "Dominance of Direct-Store-Delivery (DSD) bottling distribution networks driving prime supermarket shelf placement and cold-vault availability",
            "Strategic distribution partnerships between beverage titans (Coca-Cola, PepsiCo) and high-growth functional energy brands (Monster, Celsius)",
            "Rising adoption of sustainable 100% rPET bottles, aluminum can packaging, and smart touch-screen fountain dispensers (Coca-Cola Freestyle)"
        ]
        cust_pref_list = [
            "Zero-sugar / zero-calorie formulation with natural taste profiles and clean-label non-caloric sweeteners (Stevia / Monkfruit)",
            "Functional wellness benefits including natural green tea caffeine, essential thermogenic fat burn, electrolytes, and gut health probiotics",
            "Convenient single-serve grab-and-go cold vault availability across convenience stores, gas stations, and supermarkets",
            "Brand prestige, lifestyle alignment, and transparent nutritional disclosures without artificial preservatives"
        ]
        exciting_list = [
            f"{providers[0]['name']} global non-alcoholic concentrate model, Coca-Cola Zero Sugar, Sprite, Fairlife ultra-filtered milk, & BodyArmor hydration",
            f"{providers[1]['name']} integrated DSD beverage network, Pepsi Zero Sugar, Gatorade Fast Twitch energy, & Mountain Dew Starry",
            f"{providers[2]['name']} Monster Energy Original & Ultra line dominance, Reign Total Body Fuel, & Coca-Cola global bottling network"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} Dr Pepper trademark, Keurig single-serve coffee pod ecosystem, & Core Hydration water")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} Celsius essential energy thermogenic drinks, On-The-Go powder stick packs, & PepsiCo distribution")

        diff_list = [
            "Unrivaled Direct-Store-Delivery (DSD) bottling routes providing same-day store restocking and cold-vault dominance",
            "Iconic multi-billion-dollar brand equity portfolios driving sticky repeat consumer purchase frequency",
            "Proprietary concentrate formulations, sweetener blending tech, and high-margin fountain dispensing infrastructure",
            "Massive R&D capabilities in functional ingredients, aseptic cold-fill manufacturing, and sustainable packaging"
        ]
        comp_data = {
            "government": [
                "US FDA Food Safety Modernization Act (FSMA) & 21 CFR Food & Beverage Processing Regulations",
                "US TTB Non-Alcoholic Formula Approval & State Beverage Container Deposit Laws (Bottle Bills)",
                "EU General Food Law Regulation & Local Municipal Sugar Tax Mandates"
            ],
            "industry": [
                "ABA (American Beverage Association) Environmental & Product Safety Operational Standards",
                "ISO 22000 Food Safety Management Systems & GFSI (Global Food Safety Initiative) Auditing Standards",
                "NSF International Beverage Dispensing Equipment & Sanitation Certification"
            ],
            "segment": [
                "Aseptic PET bottle filling sterilization specifications and CO2 carbonation volume compliance",
                "Strict Brix level (sugar/solids ratio) & pH monitoring accuracy specs across high-speed bottling lines",
                "100% recyclable rPET container structural specs and post-consumer recycled material compliance"
            ]
        }
    elif is_home_improvement:
        trends_list = [
            "Project Shift & Macro Headwinds: Spending growth tightening to ~$862B (on track toward $1.29T by 2035 at 4.5% CAGR) with homeowners pivoting from major discretionary remodels to essential repairs & maintenance",
            "Aging Housing Stock & Deferred Repairs: Over 86% of homeowners deferring non-critical projects due to high interest rates, driving concentrated demand into roofing, painting, HVAC, and minor functional upgrades",
            "Retail Consolidation & Private Label Growth: Home Depot (28% share) and Lowe's (17% share) dominating Pro contractor supply chains while private-label hand tools & lawn/garden brands gain high-margin market share",
            "Tech Integration & AR/VR Visualization: 25%+ consumer adoption of AR/VR product visualization apps, smart home device integration, and voice/AI-driven supply chain optimization"
        ]
        cust_pref_list = [
            "Availability of high-quality essential repair materials (roofing, plumbing, electrical) for immediate contractor & DIY pickup",
            "Competitive price-to-value ratio on professional-grade hand tools, power tools, and high-margin private-label merchandise",
            "Omnichannel retail convenience with real-time store inventory sync, BOPIS fulfillment, and Pro contractor credit rewards",
            "Interactive AR/VR room visualization tools, smart home device compatibility, and expert in-store trade advice"
        ]
        exciting_list = [
            f"{providers[0]['name']} Pro Extra contractor ecosystem, HD Supply MRO distribution, and exclusive Husky/Rigid professional tool line",
            f"{providers[1]['name']} MVPs Pro Rewards platform, Kobalt & Craftsman tool portfolios, and Total Home Installation Services",
            f"{providers[2]['name']} specialty hard-surface flooring scale (LVP, natural stone, tile) and Pro Premier installation supplies"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} rural lifestyle, land maintenance, fencing, and farm hardware distribution network")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} specialty pool & spa care chemicals, water testing tech, and maintenance services")

        diff_list = [
            "Dominant Pro contractor distribution network and dedicated Pro Extra / MVPs commercial loyalty platforms",
            "Extensive store footprint providing strategic last-mile same-day fulfillment and bulky item delivery",
            "High-margin exclusive private-label brand portfolios (Husky, Kobalt, Craftsman) driving customer lock-in",
            "Advanced omnichannel inventory sync and AR/VR spatial visualization software"
        ]
        comp_data = {
            "government": [
                "US Consumer Product Safety Commission (CPSC) Power Tool & Equipment Safety Regulations",
                "US EPA Lead-Safe Certified Renovation, Repair & Painting (RRP) Standards",
                "US OSHA Retail Warehouse & Heavy Material Handling Operational Guidelines"
            ],
            "industry": [
                "NRF (National Retail Federation) & HIMA (Home Improvement Manufacturers Association) Standards",
                "PCI-DSS v4.0 Retail Store POS Payment Security Compliance",
                "ANSI (American National Standards Institute) Power Tool & Hardware Safety Specifications"
            ],
            "segment": [
                "Real-time store inventory synchronization accuracy (>99%) across e-commerce & store POS",
                "Pro contractor order fulfillment SLA (<2 hours for store BOPIS / same-day job site delivery)",
                "EPA Lead-Safe & Chemical SDS (Safety Data Sheet) regulatory compliance documentation"
            ]
        }
    elif is_lodging:
        trends_list = [
            "Widespread deployment of Artificial Intelligence (AI) and generative LLM booking agents across hotel operations for dynamic pricing, automated guest service, and labor cost optimization",
            "Market bifurcation and 'Premiumization': Luxury & lifestyle hotel tiers outperforming while economy segments face demand pressure, driving asset-light conversions and brand consolidation",
            "Shift in traveler intentions toward 'Whycation' purpose-driven travel, holistic wellness retreats, and authentic, culturally immersive local experiences",
            "Operational shift prioritizing net operating profit over top-line RevPAR through labor automation, energy management tech, and mega-event travel capture (FIFA 2026)"
        ]
        cust_pref_list = [
            "Seamless AI-powered mobile booking, instant concierge messaging, and keyless smartphone room access eliminating check-in friction",
            "High-value loyalty program flexibility (Bonvoy, Honors, World of Hyatt) with guaranteed room upgrades and experiential reward redemption",
            "Refreshed wellness amenities, eco-friendly regenerative hospitality practices, and authentic local food & beverage programming",
            "Transparent pricing with no hidden resort fees, flexible cancellation policies, and high-speed multi-device Wi-Fi"
        ]
        exciting_list = [
            f"{providers[0]['name']} global hotel portfolio, luxury tier dominance, AI dynamic pricing engine, and industry-leading loyalty platform",
            f"{providers[1]['name']} high-margin asset-light franchise expansion, digital guest app integration, and select-service scale",
            f"{providers[2]['name']} premier luxury, lifestyle, & all-inclusive resort portfolio and high-engagement member loyalty ecosystem"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} prime urban & resort hotel real estate assets undergoing strategic capital enhancement")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} global economy & midscale lodging franchise network delivering accessible travel value")

        diff_list = [
            "Unrivaled global hotel footprint and brand portfolio breadth spanning economy to ultra-luxury tiers",
            "Massive loyalty program scale driving low customer acquisition costs and direct mobile app booking margins",
            "Asset-light franchise and management business models generating predictable high-margin recurring fee streams",
            "Advanced AI revenue management systems optimizing occupancy yield and labor efficiency"
        ]
        comp_data = {
            "government": [
                "US ADA (Americans with Disabilities Act) Hospitality Accessibility Standards",
                "US OSHA Workplace Safety & Hotel Housekeeping Operational Mandates",
                "EU GDPR & Local Tax Governance Regulations for Hotel Guest Data"
            ],
            "industry": [
                "AHLA (American Hotel & Lodging Association) Operational & Safety Standards",
                "PCI-DSS v4.0 Hotel Property Management System (PMS) Payment Security Compliance",
                "ISO 22000 Food Safety Management Systems for Hotel Food & Beverage Operations"
            ],
            "segment": [
                "Hotel Property Management System (PMS) integration with direct booking engine (<1 sec availability sync)",
                "Digital key Bluetooth Low Energy (BLE) lock response latency (<500ms room door unlock)",
                "99.9% uptime for central reservation systems (CRS) and guest loyalty point processing APIs"
            ]
        }
    elif is_retail:
        trends_list = [
            "Accelerated adoption of omnichannel retail integration blending physical department store showrooms with unified digital mobile e-commerce platforms",
            "Expansion of off-price, curated luxury, and private-label fashion brands driving resilient gross margin performance amid shifting consumer discretionary spending",
            "Deployment of AI-driven hyper-personalized marketing, automated inventory demand forecasting, and smart supply chain fulfillment",
            "Shift toward experiential store formats, hassle-free buy-online-pickup-in-store (BOPIS) services, and seamless digital return logistics"
        ]
        cust_pref_list = [
            "Curated product assortments featuring exclusive national brands, trending designer apparel, and high-quality private-label goods",
            "Seamless omnichannel shopping flexibility with instant store inventory visibility, fast home delivery, and effortless in-store returns",
            "Personalized loyalty rewards programs, targeted promotional discounts, and flexible store card financing terms",
            "High-touch customer service, store ambiance, and low-friction friction-free mobile checkout solutions"
        ]
        exciting_list = [
            f"{providers[0]['name']} nationwide retail footprint, omnichannel digital platform, and exclusive brand partnerships",
            f"{providers[1]['name']} off-price apparel scale, rapid inventory turnover, and compelling treasure-hunt shopping experience",
            f"{providers[2]['name']} premium department store customer service, loyalty rewards network, and luxury brand curation"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} e-commerce fulfillment infrastructure, targeted digital marketing, and private-label apparel")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} value-oriented discount store pricing, localized distribution networks, and customer loyalty")

        diff_list = [
            "Extensive nationwide physical retail real estate footprint providing strategic last-mile store fulfillment and BOPIS hubs",
            "Deep long-standing vendor relationships and exclusive brand distribution agreements inaccessible to digital-only competitors",
            "Proprietary customer loyalty data platforms driving highly targeted personalized promotional campaigns and high repeat spend",
            "Advanced inventory management and supply chain logistics optimizing sell-through rates and reducing markdown risks"
        ]
        comp_data = {
            "government": [
                "US FTC Consumer Protection & Truth-in-Advertising Guidelines",
                "US OSHA Workplace Safety & Retail Warehouse Operational Standards",
                "US CPSIA (Consumer Product Safety Improvement Act) Apparel & Goods Regulations"
            ],
            "industry": [
                "NRF (National Retail Federation) Omnichannel & Data Exchange Standards",
                "PCI-DSS v4.0 Store POS Payment Terminal Security Compliance",
                "ISO 9001 Supply Chain & Merchandise Quality Management Systems"
            ],
            "segment": [
                "Same-day store inventory synchronization accuracy (>99%) across e-commerce & POS systems",
                "BOPIS order fulfillment SLA (<2 hours from online order placement)",
                "Customer Data Platform (CDP) privacy compliance (CCPA / CPRA / GDPR)"
            ]
        }
    elif is_media:
        trends_list = [
            "Accelerated secular migration of viewers and ad dollars from linear cable TV to direct-to-consumer (DTC) streaming (SVOD/AVOD) and free ad-supported streaming TV (FAST)",
            "Skyrocketing live sports broadcasting rights valuation and aggressive bidding by DTC streaming platforms for NFL, NBA, and live sports rights",
            "Rapid adoption of hybrid subscription models combining ad-tier monetization, password-sharing controls, and AI-driven personalized recommendation engines",
            "Consolidation across major studio networks, digital news channels, and live event production to build scale against tech-native streaming giants"
        ]
        cust_pref_list = [
            "High-quality original content, live news, and exclusive live sports broadcasting accessible seamlessly across smart TVs and mobile devices",
            "Low-friction subscription management, transparent pricing, and low-cost ad-supported membership options",
            "Sub-second video playback latency, adaptive 4K HDR streaming quality, and reliable live event streaming uptime",
            "Interactive news coverage, personalized programming feeds, and social community sharing features"
        ]
        exciting_list = [
            f"{providers[0]['name']} flagship broadcast network, cable news channels, live sports coverage, and FAST streaming platforms",
            f"{providers[1]['name']} premium entertainment studios, direct-to-consumer streaming catalogs, and live event ticketing scale",
            f"{providers[2]['name']} top-tier linear broadcast station networks, national news programming, and multi-platform media content"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} extensive affiliate TV station network, sports broadcasting, and digital video advertising")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} regional broadcast stations, news production facilities, and digital streaming news feeds")

        diff_list = [
            "Massive news & sports broadcasting rights portfolios creating sticky daily viewer engagement and multi-channel brand loyalty",
            "Dual-revenue stream monetization combining retransmission consent / carriage fees with high-CPM digital advertising",
            "Extensive local and national broadcast station coverage reaching over 90% of US television households",
            "Decades-long brand authority in journalism, live entertainment production, and global content syndication"
        ]
        comp_data = {
            "government": [
                "US Federal Communications Commission (FCC) Broadcast Licensing & Spectrum Ownership Regulations",
                "US FTC & DOJ Antitrust Guidelines for Media Mergers & Content Syndication",
                "EU Audiovisual Media Services Directive (AVMSD) & Local Content Quotas"
            ],
            "industry": [
                "NAB (National Association of Broadcasters) Technical & Transmission Standards",
                "ATSCA/3.0 NextGen TV Interactive Broadcast Standards",
                "Nielsen & Comscore Cross-Platform Audience Measurement Standards"
            ],
            "segment": [
                "FCC 21 CFR / Children's Television Act Compliance & Broadcast Decency Mandates",
                "Sub-2 second video start times and 99.99% CDN edge delivery uptime for live video streaming",
                "Closed Captioning (CEA-608/708) & CALM Act Loudness Commercial Compliance"
            ]
        }
    elif is_defense:
        trends_list = [
            "Escalating adoption of Unmanned Aerial Systems (UAS / Drones), low-cost kamikaze loitering munitions, and electronic warfare (EW) counter-drone technologies across modern defense forces",
            "Urgent allied recapitalization and replenishment of precision-guided munitions (HIMARS, Patriot PAC-3, NASAMS, 155mm artillery shell production) driven by high depletion rates in contemporary operational theaters",
            "Rapid shift toward integrated multi-domain command & control (JADC2), AI-driven target recognition, and autonomous swarming drone operational doctrine",
            "Broad expansion of defense procurement budgets across US, NATO, European, and Indo-Pacific allies addressing high-intensity peer combat readiness, air defense, and deterrence"
        ]
        cust_pref_list = [
            "Proven battlefield combat efficacy and operational reliability under active electronic warfare (EW) jamming and GPS-denied environments",
            "Low-cost, high-volume drone attrition capacity balanced with high-end stealth, sensor fusion, and multi-spectral counter-drone defenses",
            "Rapid surge production manufacturing capacity and resilient defense supply chains capable of scaling production under tight procurement deadlines",
            "Interoperability with NATO digital battle management communications, open-architecture avionics, and modular mission payloads"
        ]
        exciting_list = [
            f"{providers[0]['name']} land combat armored vehicles, nuclear submarine production scale, and tactical communications systems",
            f"{providers[1]['name']} Patriot air & missile defense systems, NASAMS integrated air defense, and Pratt & Whitney propulsion technologies",
            f"{providers[2]['name']} HIMARS precision rocket artillery, PAC-3 missile interceptors, and F-35 stealth strike fighter combat capability"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} heavy-lift rotorcraft, aerial refuelers, and space/satellite defense architectures")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} B-21 Raider next-gen stealth bomber and autonomous loitering drone systems")

        diff_list = [
            "Extensive battlefield combat validation and combat-proven reliability across high-intensity modern operational environments",
            "Proprietary stealth technology, advanced radar/sensor fusion, and cyber-hardened electronic warfare countermeasures",
            "Exclusive prime contractor status on multi-billion dollar long-term government defense programs of record",
            "Unrivaled defense industrial manufacturing base, complex system integration, and global logistics support"
        ]
        comp_data = {
            "government": [
                "US Department of Defense Federal Acquisition Regulation Supplement (DFARS) & ITAR Export Controls",
                "US DoD Cybersecurity Maturity Model Certification (CMMC 2.0) Mandatory Supplier Standards",
                "NATO Standardisation Agreements (STANAG) for Munitions, Drones & Tactical Data Links"
            ],
            "industry": [
                "AS9100 Rev D Aerospace & Defense Quality Management System Requirements",
                "ISO 9001 Quality Management & MIL-STD-810 Environmental Engineering Considerations",
                "NIST SP 800-171 Protecting Controlled Unclassified Information (CUI) in Defense Systems"
            ],
            "segment": [
                "MIL-STD-461 Electromagnetic Compatibility & Electronic Warfare (EW) Jamming Hardening Specs",
                "GPS-denied Inertial Navigation System (INS) precision specs & encrypted M-Code satellite telemetry",
                "High-intensity ordinance storage safety specs (MIL-STD-2105 Hazard Assessment for Munitions)"
            ]
        }
    elif is_energy:
        trends_list = [
            "Escalating global geopolitical instability and heightened crude supply security concerns surrounding critical maritime chokepoints and regional supply disruptions",
            "Accelerated long-term Liquefied Natural Gas (LNG) contracting and export terminal infrastructure expansion across North America and Europe",
            "Strict capital discipline focusing on high-margin low-breakeven Permian Basin and deepwater assets while prioritizing shareholder dividends and buybacks",
            "Dual-track strategy balancing near-term oil and gas supply security with strategic long-term investments in Carbon Capture & Storage (CCS) and hydrogen"
        ]
        cust_pref_list = [
            "Guaranteed supply security and geopolitical risk mitigation through multi-region integrated supply networks insulated from localized crude trade disruptions",
            "Flexible long-term commercial supply contracts with robust crude oil price hedging and destination flexibility",
            "High refined product quality meeting strict global environmental specs (IMO 2020 low-sulfur marine fuel, ultra-low sulfur diesel, aviation jet fuel)",
            "End-to-end midstream pipeline and deepwater export terminal access ensuring low logistics costs and fast delivery turnaround"
        ]
        exciting_list = [
            f"{providers[0]['name']} Permian Basin manufacturing scale, sub-$35/bbl breakeven assets, and Guyana deepwater mega-projects",
            f"{providers[1]['name']} world-scale Tengizchevroil expansion and accretive deepwater asset integration",
            f"{providers[2]['name']} market-leading global LNG trading portfolio and integrated energy marketing network"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} multi-energy strategy combining LNG market leadership with renewable power integration")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} resilient upstream crude production coupled with high-growth bioenergy and EV charging infrastructure")

        diff_list = [
            "Geographic diversification and multi-region upstream assets mitigating regional supply chokepoint exposures and geopolitical volatility",
            "Massive capital balance sheet strength with low-breakeven operations allowing sustained deployment across volatile price cycles",
            "Complete end-to-end integration from upstream exploration & production to midstream logistics, refining, and global retail distribution",
            "Proprietary refining technology, high-volume chemical integration, and advanced carbon capture scale"
        ]
        comp_data = {
            "government": [
                "US EPA Clean Air Act & Renewable Fuel Standard (RFS) Mandates",
                "US Bureau of Safety and Environmental Enforcement (BSEE) Offshore Deepwater Safety Regulations",
                "EU Corporate Sustainability Due Diligence Directive (CSDDD) & Methane Import Regulations"
            ],
            "industry": [
                "American Petroleum Institute (API) Spec Q1 / Q2 Quality Management Standards",
                "ISO 14001 Environmental Management System & ISO 45011 Occupational Health & Safety",
                "IMO 2020 International Maritime Organization Low-Sulfur Fuel Regulations"
            ],
            "segment": [
                "Pipeline batch fuel purity specifications (ASTM D4814 gasoline, ASTM D975 diesel, ASTM D1655 Jet A-1)",
                "LNG cryogenic storage and transport specifications (-162°C at atmospheric pressure)",
                "Upstream methane flare and venting intensity compliance limits (<0.2% total production)"
            ]
        }
    elif is_pharma:
        trends_list = [
            "Surge in demand for GLP-1 receptor agonists for obesity, diabetes, and metabolic cardiovascular health",
            "Rapid shift toward targeted immuno-oncology, antibody-drug conjugates (ADCs), and cell/gene therapies",
            "Integration of AI/ML in de novo drug discovery, protein folding predictions, and clinical trial optimization",
            "Increasing patent cliff pressure driving aggressive M&A and biosimilar market entries"
        ]
        cust_pref_list = [
            "High efficacy and superior safety profiles with minimal adverse side effects",
            "Patient convenience via oral small-molecule formulations or subcutaneous auto-injectors",
            "Strong clinical trial data demonstrating overall survival (OS) and quality-of-life benefits",
            "Favorable insurance reimbursement coverage and patient assistance access programs"
        ]
        exciting_list = [
            f"{providers[0]['name']} GLP-1 / targeted therapeutic platform delivering high efficacy",
            f"{providers[1]['name']} oncology & immunology portfolio expanding patient access",
            f"{providers[2]['name']} next-gen biologics replacing legacy standard-of-care treatments"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} immuno-oncology blockbuster survival metrics")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} radioligand and precision medicine pipeline")

        diff_list = [
            "Extensive global patent protection and deep intellectual property moats",
            "Massive R&D capital scale ($10B+ annually per leader) and high-throughput screening capability",
            "Decades-long relationships with global healthcare providers, regulatory bodies, and insurers",
            "Advanced biologics manufacturing infrastructure capable of complex sterile liquid production"
        ]
        comp_data = {
            "government": [
                "US FDA New Drug Application (NDA) & Biologics License Application (BLA) Regulatory Approval Standards",
                "European Medicines Agency (EMA) Centralised Marketing Authorization Guidelines",
                "US Inflation Reduction Act (IRA) Medicare Drug Price Negotiation Provisions"
            ],
            "industry": [
                "Current Good Manufacturing Practice (cGMP) Quality Standards for Pharmaceuticals",
                "ICH (International Council for Harmonisation) Technical Requirements for Pharmaceuticals",
                "ISO 13485 Medical Devices & Drug Delivery Combination Product Standards"
            ],
            "segment": [
                "Strict cold-chain logistics & temperature-controlled transport storage specifications (2°C to 8°C / -80°C)",
                "FDA 21 CFR Part 11 Electronic Records & Signature Compliance for Clinical Data",
                "HIPAA / GDPR Data Privacy Requirements for Patient Health Information (PHI) in Clinical Trials"
            ]
        }
    elif is_auto:
        trends_list = [
            "Accelerating transition from internal combustion engines (ICE) to Battery Electric Vehicles (BEV) and Hybrids",
            "Integration of level-2+ and level-3 autonomous driving software",
            "Rising adoption of software-defined vehicle (SDV) architectures and over-the-air (OTA) updates",
            "Focus on high-margin ultra-luxury segment pricing power and custom electrification platforms"
        ]
        cust_pref_list = [
            "Long driving range per charge (>300 miles) and sub-20 minute fast-charging capabilities",
            "High safety ratings, driver assistance features, and active collision avoidance",
            "Seamless smartphone integration, touch UI infotainment, and connected app telemetry",
            "Total Cost of Ownership (TCO) parity with conventional gas-powered vehicles"
        ]
        exciting_list = [
            f"{providers[0]['name']} full-stack neural net AI and gigafactory manufacturing scale",
            f"{providers[1]['name']} hybrid powertrain reliability & solid-state battery R&D",
            f"{providers[2]['name']} modular EV architecture and hands-free highway autopilot"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} high-performance hybrid powertrains and brand equity")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} commercial fleet software & electric utility trucks")

        diff_list = [
            "Proprietary battery chemistry and gigafactory manufacturing scale",
            "Global charging network infrastructure and integrated software ecosystems",
            "Decades of automotive manufacturing precision, dealer network reach, and brand loyalty",
            "High pricing power and exclusivity in high-performance luxury automotive tiers"
        ]
        comp_data = {
            "government": [
                "National Highway Traffic Safety Administration (NHTSA) Federal Motor Vehicle Safety Standards (FMVSS)",
                "EPA & EU Fleet Carbon Emission Target Regulations & Zero-Emission Vehicle (ZEV) Mandates",
                "US Inflation Reduction Act (IRA) Clean Vehicle Tax Credit Supply Chain Requirements"
            ],
            "industry": [
                "ISO 26262 Road Vehicles Functional Safety Standards",
                "ISO/SAE 21434 Cybersecurity Engineering for Road Vehicles",
                "Automotive SPICE (Software Process Improvement and Capability dEtermination) Compliance"
            ],
            "segment": [
                "High-voltage battery safety specifications (UN 38.3 transport & thermal runaway protection)",
                "Standardized charging port specs (NACS / CCS Type 1 & 2 compatibility)",
                "Sub-100ms vehicle CAN bus / Automotive Ethernet communication latency standards"
            ]
        }
    elif is_financial:
        trends_list = [
            "Surge in consumer adoption of contactless NFC tap-to-pay, digital wallet tokenization (Apple Pay, Google Wallet), and embedded finance gateways",
            "Rapid deployment of AI-driven real-time fraud monitoring, automated chargeback resolution, and transaction risk scoring engines",
            "Expanding regulatory mandates for Open Banking APIs and Payment Services Directive 3 (PSD3) Strong Customer Authentication (SCA)",
            "Acceleration of cross-border real-time multi-currency settlement networks and instant account-to-account (A2A) clearing infrastructure"
        ]
        cust_pref_list = [
            "Sub-second transaction authorization speeds with zero-friction checkout experiences across global online and point-of-sale (POS) terminals",
            "Zero-liability fraud protection guarantees and multi-factor biometric security authentication shielding cardholder identities",
            "Universal merchant acceptance at over 100 million locations worldwide with multi-currency dynamic conversion options",
            "Generous cashback rewards, premium travel benefits, flexible revolving credit terms, and transparent fee structures"
        ]
        exciting_list = [
            f"{providers[0]['name']} global payment processing network handling over 200 billion annual authorization transactions",
            f"{providers[1]['name']} Cyber & Intelligence AI solutions and open-banking financial technology infrastructure",
            f"{providers[2]['name']} premium closed-loop credit network driving industry-leading merchant spend volume and loyalty rewards"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} digital wallet ecosystem and merchant payment gateway platform")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} consumer credit card issuing, digital banking, and proprietary credit decisioning algorithms")

        diff_list = [
            "Unrivaled two-sided network effects connecting hundreds of millions of cardholders to tens of millions of active merchants globally",
            "Massive transaction scale capable of processing tens of thousands of secure payment messages per second with 99.999% uptime",
            "Deep multi-decade bank issuing partnerships, co-branded network affiliations, and extensive global regulatory compliance moats",
            "State-of-the-art tokenization security, Hardware Security Module (HSM) encryption, and continuous AI fraud prevention infrastructure"
        ]
        comp_data = {
            "government": [
                "US CFPB & Federal Reserve Regulations: Regulation Z (Truth in Lending), Regulation E (EFT), & Fair Credit Reporting Act (FCRA)",
                "US Bank Secrecy Act (BSA), FinCEN Customer Due Diligence (CDD), & OFAC Global Sanctions Enforcement",
                "EU Payment Services Directive 3 (PSD3) & GDPR Data Sovereignty Mandates"
            ],
            "industry": [
                "PCI-DSS v4.0 (Payment Card Industry Data Security Standard) Mandatory Processing & Storage Controls",
                "ISO/IEC 27001 Information Security Management & Third-Party SOC 2 Type II Cloud Audit Certification",
                "EMVCo Global Interoperability Specifications & 3-D Secure (3DS 2.0) E-Commerce Authentication Protocols"
            ],
            "segment": [
                "Sub-100ms ISO 8583 / ISO 20022 payment authorization and clearing message processing SLAs",
                "99.999% High Availability with active-active multi-region data center failover (zero RPO)",
                "Hardware Security Module (HSM) key management, EMV network tokenization, and end-to-end payload encryption (E2EE)"
            ]
        }
    else:
        trends_list = [
            f"Surge in capital expenditure for next-gen {segment_clean} technology",
            "Rapid deployment of AI-driven optimization and automated workflow management",
            "Supply chain resilience and regional manufacturing localization",
            "Emphasis on environmental sustainability and energy efficiency metrics"
        ]
        cust_pref_list = [
            "Extreme precision, high uptime guarantees, and low failure rates",
            "Integrated end-to-end solutions with deep software compatibility",
            "Pay-as-you-scale commercial terms and lower total cost of ownership",
            "Robust global technical field support and spare parts availability"
        ]
        exciting_list = [
            f"{providers[0]['name']} market leading platform delivering unmatched precision",
            f"{providers[1]['name']} automated self-monitoring architectures and fault diagnosis",
            f"{providers[2]['name']} proprietary hardware-software co-design delivering peak benchmarks"
        ]
        if len(providers) > 3:
            exciting_list.append(f"{providers[3]['name']} seamless plug-and-play integration with legacy systems")
        if len(providers) > 4:
            exciting_list.append(f"{providers[4]['name']} high-reliability process control and yield management")

        diff_list = [
            "Extensive IP portfolio and multi-decade research and development moats",
            "Deep strategic partnerships with top tier-1 global enterprise clients",
            "High customer switching costs and sticky ecosystem integration",
            "Unrivaled manufacturing scale and high-precision quality control"
        ]
        comp_data = {
            "government": [
                "US & EU Strategic Export Controls and Trade Regulations",
                "Environmental Protection Agency (EPA) & REACH Chemical Directives",
                "National Infrastructure Protection & Data Privacy Standards"
            ],
            "industry": [
                "ISO 9001 Quality Management & ISO 14001 Environmental Standards",
                "Global Industry Consortium Safety & Reliability Guidelines",
                "Third-Party SOC 2 Type II Security & Data Audit Compliance"
            ],
            "segment": [
                "High-availability operational uptime SLAs (99.9%+) and system response time benchmarks",
                "Interoperability & standardized protocol communication specifications",
                "Disaster recovery, data redundancy, and business continuity compliance specifications"
            ]
        }

    # Derive MVP and Winning Product Specs based on competitive research
    if is_farm_products:
        mvp_specs = [
            f"Core Agricultural Commodity Output: Standard grain or oilseed harvesting meeting baseline USDA grade standards and moisture specifications",
            f"Basic Chemical Formulation: Standard synthetic pesticide or fertilizer formulation meeting EPA FIFRA registration requirements",
            f"Standard Bulk Distribution: Standard rail hopper car or river barge bulk transport with basic grain elevator storage",
            f"Baseline Regulatory Filing: Baseline USDA/EPA chemical registration and standard phytosanitary certification"
        ]
        winning_specs = [
            f"Biotech Seed Trait Innovation & Gene Editing ({providers[0]['name']}): High-yield germplasm with multi-mode herbicide tolerance (Enlist) and insect protection (Vorceed) without yield penalty",
            f"Global Processing & Bioenergy Scale: High-efficiency automated oilseed crushing facilities producing low-carbon renewable diesel feedstock and protein meal",
            f"Biological Crop Protection & Nitrogen Management: Bio-based fungicide and biostimulant formulations reducing synthetic chemical runoff and improving soil health",
            f"Digital Agronomy & Traceable Circular Economy: Integrated AI digital farming platform (Granular/Climate FieldView) offering real-time field analytics and carbon credit certification"
        ]
    elif is_discount_stores:
        mvp_specs = [
            f"Core Discount Retail & POS: E-commerce web storefront and physical store POS terminal handling standard barcode checkout and payment clearing",
            f"Basic Inventory Visibility: Daily batch inventory sync updating product availability across physical stores and warehouse fulfillment centers",
            f"Standard Order Fulfillment: Standard 3-5 day home delivery shipping with email order tracking and basic store return processing",
            f"Baseline Value Loyalty: Basic digital weekly ad circular and simple point-per-dollar spending tracker"
        ]
        winning_specs = [
            f"Frictionless Curbside & BOPIS Fulfillment ({providers[0]['name']}): Real-time store inventory sync enabling Drive Up / BOPIS within <2 hours and automated parking bay notification",
            f"High-Margin Private-Label Brand Ecosystem: Exclusive multi-billion-dollar private label lines (Kirkland Signature / Great Value / Good & Gather) delivering high margins",
            f"Automated Supply Chain & Micro-Fulfillment: Automated distribution center sorters and robotics driving lowest cost-per-case store stocking overhead",
            f"Integrated Retail Media Network: Target Circle / Walmart+ subscriber monetization leveraging first-party shopper purchase data for high-margin advertising"
        ]
    elif is_wineries:
        mvp_specs = [
            f"Core Distilling / Wine Bottling: Standard column-still spirit distillation or bulk wine blending meeting baseline FDA / TTB alcohol safety limits",
            f"Basic Wholesale Distribution: Standard 750ml glass bottle packaging with paper labeling and 3-5 day wholesale distributor delivery",
            f"Standard Retail Placement: Baseline retail shelf placement across licensed liquor stores and supermarkets",
            f"Essential TTB Compliance: TTB COLA label certification, proof hydrometer testing, and basic state ABC license registration"
        ]
        winning_specs = [
            f"Master Distiller Aging & Brand Equity ({providers[0]['name']}): Multi-year charred oak barrel aging program (Johnnie Walker / Jack Daniel's / Woodford Reserve) driving high pricing power",
            f"Super-Premium Agave & Terroir Sourcing: 100% Blue Weber Agave estate farming (Don Julio / Casamigos) and single-estate Napa Valley terroir grape cultivation (Duckhorn / Decoy)",
            f"High-Margin Canned RTD Spirit Cocktail Integration: Spirit-based canned cocktails (Jack & Coke / High Noon) capturing retail grab-and-go growth",
            f"Direct-to-Consumer (DTC) Wine Club & Anti-Counterfeit Tech: DTC wine club subscription platform and RFID/NFC bottle authentication for ultra-luxury vintages"
        ]
    elif is_beverages:
        mvp_specs = [
            f"Core Soft Drink Bottling: Standard carbonated soft drink formulation meeting basic FDA 21 CFR safety limits and standard high-fructose corn syrup (HFCS) sweetening",
            f"Basic Retail Packaging: Standard 12oz aluminum cans and 2-liter PET bottles with baseline paper label branding",
            f"Standard Warehouse Distribution: 3-5 day wholesale warehouse delivery to regional grocery distributors and retail buyers",
            f"Essential Compliance: Baseline nutrition facts labeling, allergen disclosure, and standard FDA facility registration"
        ]
        winning_specs = [
            f"Zero-Sugar Proprietary Sweetener & DSD Scale ({providers[0]['name']}): Zero-sugar taste parity formula (Coca-Cola Zero / Pepsi Zero) backed by sub-24h Direct-Store-Delivery (DSD) restocking",
            f"Functional Energy & Electrolyte Formulation: Thermogenic green-tea caffeine blend (Celsius / Monster) and multi-electrolyte isotonic hydration (Gatorade / BodyArmor)",
            f"Sustainable Packaging Innovation: 100% rPET post-consumer recycled bottles and lightweight infinitely recyclable aluminum cans",
            f"Omnichannel Fountain & D2C Integration: Touch-screen interactive fountain dispensers (Freestyle) and automated mobile app D2C pod subscriptions"
        ]
    elif is_home_improvement:
        mvp_specs = [
            f"Core Retail & Pro Commerce: E-commerce storefront & mobile app featuring basic building material catalog browsing, store directory, and checkout payment gateway",
            f"Basic Inventory Visibility: Daily batch inventory synchronization updating product stock across physical retail stores and warehouse fulfillment centers",
            f"Standard Order Delivery: Standard 3-5 day parcel shipping with email confirmation and basic in-store customer return processing",
            f"Baseline Trade Contractor Loyalty: Basic contractor account registration with manual volume discount calculation and paper receipt tracking"
        ]
        winning_specs = [
            f"Pro Contractor High-Volume Distribution ({providers[0]['name']}): Dedicated Pro Extra / MVPs portal with real-time job site material delivery tracking, bulk pricing tiers, and credit integration",
            f"Omnichannel Real-Time Inventory & BOPIS: Sub-second store inventory sync supporting Buy-Online-Pickup-In-Store (BOPIS) within <2 hours and curbside drive-thru pickup",
            f"AR/VR Spatial Visualization & Smart Tech Integration: AR/VR mobile room visualization for flooring/paint/cabinetry and voice/AI-driven smart home device integration",
            f"High-Margin Private Label Tool & Hardware Portfolio: Exclusive professional-grade private tool brand lock-in (Husky, Kobalt, Craftsman) with lifetime warranty exchange"
        ]
    elif is_lodging:
        mvp_specs = [
            f"Core Reservation Engine: Direct web/mobile room booking interface with basic room availability calendar and standard credit card payment",
            f"Basic Property Operations: Standalone Property Management System (PMS) handling manual front-desk guest check-in/out and room housekeeping status",
            f"Standard Guest Amenities: Baseline in-room amenities, physical plastic keycard room entry, and standard guest Wi-Fi access",
            f"Essential Hospitality Compliance: Local hotel tax reporting, basic guest privacy data storage, and ADA physical room compliance"
        ]
        winning_specs = [
            f"Seamless Digital Guest Journey ({providers[0]['name']}): Mobile app check-in/checkout with Bluetooth digital keyless room entry (<500ms door unlock) and personalized room preference controls",
            f"Global Loyalty Engine & Direct Booking Capture: Multi-tiered loyalty rewards platform (Bonvoy/Honors) driving direct mobile app bookings and reducing OTA commission costs",
            f"AI-Driven Dynamic Revenue Management: Automated real-time room pricing and yield management algorithms optimizing RevPAR across peak & off-peak seasons",
            f"Asset-Light Scalable Franchise Integration: Turnkey cloud-based Property Management System (PMS) enabling rapid hotel brand conversions and owner ROI"
        ]
    elif is_retail:
        mvp_specs = [
            f"Core Retail Commerce: E-commerce web/mobile storefront with standard catalog browsing, checkout payment gateway, and store directory",
            f"Basic Inventory Visibility: Daily batch inventory sync updating product availability across physical stores and web channel",
            f"Standard Order Fulfillment: Standard 3-5 day home delivery shipping with email order confirmation and manual store return processing",
            f"Baseline Customer Loyalty: Simple point-per-dollar spending tracker with standard promotional email newsletter"
        ]
        winning_specs = [
            f"Omnichannel Seamless Fulfillment ({providers[0]['name']}): Real-time sub-second inventory sync enabling Buy-Online-Pickup-In-Store (BOPIS) within <2 hours and curbside fulfillment",
            f"AI-Powered Hyper-Personalization: Real-time customer data platform (CDP) driving predictive recommendations, dynamic promotional pricing, and customized mobile app feeds",
            f"Curated Private-Label & Exclusive Brand Ecosystem: Exclusive national designer partnerships and high-margin private fashion label integration",
            f"Frictionless Checkout & Loyalty Integration: One-touch mobile NFC payment, instant store credit card decisioning, and automated frictionless return kiosks"
        ]
    elif is_media:
        mvp_specs = [
            f"Core Broadcast & Streaming: Standard 1080p HD video streaming with basic linear channel broadcast distribution",
            f"Basic Catalog & Player: On-demand video library with standard play/pause UI, basic search, and web/mobile browser support",
            f"Standard Subscription Billing: Flat monthly subscription fee with standard credit card payment processing",
            f"Essential Compliance: Standard closed captioning (CEA-608) and basic content rating disclaimers"
        ]
        winning_specs = [
            f"Ultra-High Performance Video Delivery ({providers[0]['name']}): Adaptive 4K HDR / Dolby Vision streaming with sub-2 second video start time and 99.99% global CDN edge delivery SLA",
            f"Hybrid Monetization & Ad-Tech Engine: Dynamic high-CPM ad insertion (AVOD/FAST), automated password sharing controls, and tier-1 live sports rights integration",
            f"AI Content Personalization & Recommendation: Deep learning recommendation engine driving maximum session duration and personalized content discovery",
            f"Cross-Platform Ubiquity & Live Sports: Seamless smart TV, mobile, & console app parity with multi-view live sports and interactive social streams"
        ]
    elif is_defense:
        mvp_specs = [
            f"Core Tactical Capability: Standard military-spec hardware meeting baseline MIL-STD-810 environmental environmental requirements",
            f"Basic Interoperability: Standard NATO tactical data link interfaces and encrypted line-of-sight voice/data communications",
            f"Essential Reliability: Operational MTBF benchmarks meeting minimum DoD program of record specifications",
            f"Regulatory Compliance: Baseline DFARS cybersecurity and ITAR export licensing compliance"
        ]
        winning_specs = [
            f"Battlefield Resilient Efficacy ({providers[0]['name']}): EW-jamming resistant GPS-denied autonomous navigation, AI target recognition, and JADC2 multi-domain integration",
            f"Surge Manufacturing Scale: High-rate automated manufacturing capacity capable of rapid production scaling under urgent operational requirements",
            f"Advanced Stealth & Sensor Fusion: Low-observable radar cross-section (RCS) design integrated with multi-spectral sensor payload fusion",
            f"Zero-Trust Cyber Resilience: CMMC 2.0 Level 3 certified cyber-hardened avionics with real-time autonomous threat detection"
        ]
    elif is_energy:
        mvp_specs = [
            f"Core Resource Extraction: Standard upstream oil & gas production meeting environmental safety limits",
            f"Basic Midstream Logistics: Standard pipeline batch transportation and atmospheric storage tank infrastructure",
            f"Standard Fuel Specs: Commercial fuel grades meeting minimum ASTM D4814 gasoline and ASTM D975 diesel requirements",
            f"Baseline Operational Safety: API Q1 quality management and basic EPA emissions compliance"
        ]
        winning_specs = [
            f"Low-Breakeven Permian & Deepwater Scale ({providers[0]['name']}): Ultra-low cost sub-$35/bbl extraction breakeven with automated drill-rig operations",
            f"Global Integrated LNG & Trading Portfolio: End-to-end cryogenic LNG liquefaction export terminals and real-time global crude trading Desk",
            f"Carbon Capture & Decarbonization Leadership: Commercial-scale Carbon Capture & Storage (CCS), hydrogen blending, and sub-0.2% methane intensity",
            f"End-to-End Value Chain Integration: Complete upstream E&P, midstream pipeline, refining, and renewable clean fuel marketing"
        ]
    elif is_pharma:
        mvp_specs = [
            f"Core Therapeutic Efficacy: Small-molecule drug candidate passing Phase I/II clinical safety trials",
            f"Basic Manufacturing Compliance: Initial cGMP small-batch drug synthesis meeting basic FDA/EMA standards",
            f"Standard Delivery Format: Traditional oral tablet formulation with standard room-temperature shelf life",
            f"Baseline Regulatory Filing: Standard New Drug Application (NDA) submission documentation"
        ]
        winning_specs = [
            f"Breakthrough Clinical Efficacy ({providers[0]['name']}): Blockbuster GLP-1 / targeted immuno-oncology biologic delivering overall survival (OS) dominance",
            f"Advanced Biologics & Combination Delivery: Pre-filled subcutaneous auto-injectors and targeted antibody-drug conjugates (ADCs)",
            f"AI-Accelerated R&D Engine: AI/ML de novo drug discovery pipeline reducing target-to-phase-I development cycles by 50%",
            f"Global Commercial & Patent Moat: Decades-long IP protection, global payer reimbursement coverage, and sterile cold-chain logistics"
        ]
    elif is_auto:
        mvp_specs = [
            f"Core Automotive Powertrain: Standard Internal Combustion Engine (ICE) or entry-level EV with ~200-mile EPA range",
            f"Basic Driver Assistance: Level 1 ADAS including standard cruise control and lane departure warning",
            f"Standard Vehicle Connectivity: Wired Apple CarPlay / Android Auto with basic digital dash cluster",
            f"Essential Safety Specs: NHTSA 5-star baseline crash test rating and standard 3-year/36k-mile warranty"
        ]
        winning_specs = [
            f"Full-Stack AI & Autonomous Driving ({providers[0]['name']}): End-to-end neural net Level-3 FSD autonomy with continuous over-the-air (OTA) software updates",
            f"Advanced Powertrain & Battery Scale: 4680 cell / solid-state battery architecture delivering >350-mile range and 15-minute ultra-fast charging",
            f"Software-Defined Vehicle (SDV) Ecosystem: High-performance zonal computing architecture with integrated subscription features and digital marketplace",
            f"Gigafactory Cost Leadership: Unibody die-cast manufacturing reducing vehicle assembly cost and enabling high gross margins"
        ]
    elif is_financial:
        mvp_specs = [
            f"Core Payment Processing: Standard credit/debit transaction clearing with 2-day batch merchant settlement",
            f"Basic POS Integration: Standard magnetic stripe and chip card authorization terminal compatibility",
            f"Standard Security: Baseline PCI-DSS v3.2 compliance and basic rule-based fraud detection",
            f"Essential Customer Service: Standard business-hour merchant support and basic online portal"
        ]
        winning_specs = [
            f"Ultra-High Speed Processing & Scale ({providers[0]['name']}): Global sub-100ms transaction authorization handling >200 billion annual messages with 99.999% uptime SLA",
            f"AI Real-Time Fraud & Tokenization Engine: Machine learning risk scoring, hardware tokenization (VTS/EMVCo), and zero-liability fraud protection",
            f"Global Two-Sided Network Effects: Universal acceptance at >100M merchant locations connected to billions of issued cards",
            f"Open Banking & Real-Time Settlement: Instant account-to-account (A2A) clearing, cross-border multi-currency settlement, and rich developer APIs"
        ]
    else:
        mvp_specs = [
            f"Core Functional Capability: Baseline {segment_clean} operational features fulfilling primary industry compliance",
            f"Essential Reliability: Standard SLA uptime (99.0% - 99.5%) and basic security/data protection protocols",
            f"Interoperability: Standard API endpoints and legacy system compatibility to enable immediate customer onboarding",
            f"Value Proposition: Competitive pricing model focused on low initial adoption cost and essential performance"
        ]
        winning_specs = [
            f"Market-Leading Performance: Sub-second latency / ultra-high precision exceeding top peer benchmarks ({providers[0]['name']})",
            f"Advanced Differentiating Features: Proprietary tech stack, AI/ML optimization, and automated workflow intelligence",
            f"Enterprise Scale & High Availability: 99.999% uptime SLAs with active-active redundant architecture and zero RPO failover",
            f"Ecosystem Lock-In & Moat: Deep multi-sided network effects, comprehensive security certifications (ISO/PCI/DFARS/cGMP), and end-to-end user experience"
        ]

    # Generate Competitor Differentiating Ratings Matrix (1-5 scale)
    # Define 4 core rating dimensions for the matrix
    matrix_criteria = [
        "Product Innovation & Tech Stack",
        "Market Reach & Brand Loyalty",
        "Cost Efficiency & Pricing Power",
        "Ecosystem Integration & Scale Moat"
    ]
    
    ratings_matrix = []
    for idx, p in enumerate(providers):
        comp_name = p['name']
        ticker = p.get('ticker', '') or comp_name
        # Deterministic dynamic score generation based on company identifier & index
        h = sum(ord(c) for c in ticker.upper())
        s1 = 3 + ((h + idx * 7) % 3)
        s2 = 3 + ((h * 3 + idx * 5) % 3)
        s3 = 3 + ((h * 5 + idx * 3) % 3)
        s4 = 3 + ((h * 7 + idx * 2) % 3)
        # Give top 2 market leaders slight boost on market reach/scale
        if idx == 0:
            s2 = min(5, s2 + 1)
            s4 = min(5, s4 + 1)
        elif idx == 1:
            s2 = min(5, s2 + 1)
        
        scores = [int(s1), int(s2), int(s3), int(s4)]
        
        ratings_matrix.append({
            "competitor": comp_name,
            "share": p['share'],
            "scores": scores,
            "overall_score": f"{sum(scores)/len(scores):.1f}"
        })

    # Build specific information sources per slide
    slide_sources = {
        1: [
            {"label": "Finviz Market Capitalization Screener", "url": "https://finviz.com/screener.ashx?v=111&o=-marketcap"},
            {"label": f"SEC EDGAR 10-K Reports ({providers[0]['name']})", "url": "https://www.sec.gov/edgar/searchedgar/companysearch"},
            {"label": f"Statista Global Market Intelligence ({segment_clean})", "url": "https://www.statista.com/"}
        ],
        2: [
            {"label": f"McKinsey & Company Industry Insights ({industry_clean})", "url": "https://www.mckinsey.com/industries"},
            {"label": "Gartner Strategic Technology & Market Trends", "url": "https://www.gartner.com/en/research"},
            {"label": "Harvard Business Review Customer Choice Drivers", "url": "https://hbr.org/"}
        ],
        3: [
            {"label": "Finviz Stock Screener & Market Cap Rankings", "url": f"https://finviz.com/quote.ashx?t={providers[0]['name'].split('(')[-1].replace(')', '') if '(' in providers[0]['name'] else ''}"},
            {"label": "Bloomberg Market Intelligence & Share Distribution", "url": "https://www.bloomberg.com/markets"},
            {"label": f"Company Investor Relations ({providers[0]['name']})", "url": "https://www.sec.gov/edgar"}
        ],
        4: [
            {"label": "Forrester Wave & Product Benchmarks Matrix", "url": "https://www.forrester.com/research/"},
            {"label": "IDC MarketScape Competitive Vendor Assessment", "url": "https://www.idc.com/research"},
            {"label": "Gartner Magic Quadrant Technology Evaluation", "url": "https://www.gartner.com/en/research"}
        ],
        5: [
            {"label": "US Federal Register & Regulatory Standards", "url": "https://www.federalregister.gov/"},
            {"label": "ISO International Organization for Standardization", "url": "https://www.iso.org/standards.html"},
            {"label": "NIST Computer Security Resource Center (CSRC)", "url": "https://csrc.nist.gov/"}
        ],
        6: [
            {"label": "Product Management Institute MVP Benchmarks", "url": "https://www.pmi.org/"},
            {"label": f"Enterprise Architecture & SLA Specifications ({segment_clean})", "url": "https://www.gartner.com/"},
            {"label": f"Leader Technical Documentation ({providers[0]['name']})", "url": "https://www.sec.gov/edgar"}
        ]
    }

    structured_trends = build_structured_trends(industry_clean, segment_clean, providers)

    slides_data = [
        {
            "slide_number": 1,
            "title": f"Executive Summary & Market Sizing ({segment_clean})",
            "subtitle": f"Macro Analysis for {segment_clean} within {industry_clean}",
            "type": "summary",
            "sources": slide_sources[1],
            "data": {
                "market_size_last_year": market_size_str,
                "yoy_growth_rate": f"+{growth_rate}%",
                "industry": industry_clean,
                "segment": segment_clean,
                "executive_takeaway": f"The {segment_clean} sector within {industry_clean} represented a {market_size_str} global market last year, expanding at an annual rate of +{growth_rate}%. Market dominance is led by {top_names_str}, driving major capital allocation into R&D and commercial expansion."
            }
        },
        {
            "slide_number": 2,
            "title": f"Market Trends & Customer Choice Drivers ({segment_clean})",
            "subtitle": f"Structured 8-Point Market Intelligence & Trends for {segment_clean} ({industry_clean})",
            "type": "trends",
            "sources": slide_sources[2],
            "data": {
                "industry": industry_clean,
                "segment": segment_clean,
                "structured_trends": structured_trends,
                "trends": trends_list,
                "customer_choice_drivers": cust_pref_list
            }
        },
        {
            "slide_number": 3,
            "title": f"Leading Products & Market Share ({segment_clean})",
            "subtitle": f"Approved Top Market Leaders in {segment_clean} ({industry_clean})",
            "type": "competitors",
            "sources": slide_sources[3],
            "data": {
                "industry": industry_clean,
                "segment": segment_clean,
                "market_share_providers": providers,
                "remaining_share": f"Specialty manufacturers, regional providers & emerging innovators in {segment_clean}",
                "leading_product_summary": f"Leading Product Highlight: {providers[0]['name']} commands the market lead with a {providers[0]['share']} market share, differentiated by its {providers[0]['key_offering']}.",
                "market_dynamics": f"The approved market leaders ({top_names_str}) command the overwhelming majority of market capitalization in {segment_clean}."
            }
        },
        {
            "slide_number": 4,
            "title": f"Product Excitement & Differentiators ({segment_clean})",
            "subtitle": f"Unique Value Drivers & Competitor Ratings Matrix for {segment_clean} ({industry_clean})",
            "type": "product_features",
            "sources": slide_sources[4],
            "data": {
                "industry": industry_clean,
                "segment": segment_clean,
                "exciting_characteristics": exciting_list,
                "differentiating_characteristics": diff_list,
                "matrix_criteria": matrix_criteria,
                "ratings_matrix": ratings_matrix
            }
        },
        {
            "slide_number": 5,
            "title": f"Mandatory Compliance & Specifications ({segment_clean})",
            "subtitle": f"Government, Industry & Technical Standards for {segment_clean} ({industry_clean})",
            "type": "compliance",
            "sources": slide_sources[5],
            "data": {
                "industry": industry_clean,
                "segment": segment_clean,
                "government_regulations": comp_data["government"],
                "industry_standards": comp_data["industry"],
                "segment_specs": comp_data["segment"]
            }
        },
        {
            "slide_number": 6,
            "title": f"Product Specification Roadmap ({segment_clean})",
            "subtitle": f"Minimum Viable Product (MVP) vs. Winning Specifications for {segment_clean} ({industry_clean})",
            "type": "product_specs",
            "sources": slide_sources[6],
            "data": {
                "industry": industry_clean,
                "segment": segment_clean,
                "mvp_specifications": mvp_specs,
                "winning_specifications": winning_specs
            }
        }
    ]

    result = {
        "status": "success",
        "industry": industry_clean,
        "segment": segment_clean,
        "slides": slides_data
    }

    if not custom_providers:
        analysis_cache[cache_key] = result
    return result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/get-competitors", methods=["POST"])
def get_competitors():
    payload = request.get_json() or {}
    industry = payload.get("industry", "").strip()
    market_segment = payload.get("market_segment", "").strip()

    if not industry or not market_segment:
        return jsonify({
            "status": "error",
            "message": "Both Industry and Market Segment inputs are required."
        }), 400

    competitors = resolve_market_leaders(industry, market_segment)
    return jsonify({
        "status": "success",
        "industry": industry,
        "market_segment": market_segment,
        "competitors": competitors
    })

@app.route("/api/lookup-ticker", methods=["POST"])
def lookup_ticker():
    payload = request.get_json() or {}
    ticker = payload.get("ticker", "").strip()

    if not ticker:
        return jsonify({
            "status": "error",
            "message": "Stock symbol (ticker) is required."
        }), 400

    res = lookup_finviz_ticker(ticker)
    return jsonify({
        "status": "success",
        **res
    })

@app.route("/api/analyze", methods=["POST"])
def analyze():
    payload = request.get_json() or {}
    industry = payload.get("industry", "").strip()
    market_segment = payload.get("market_segment", "").strip()
    custom_providers = payload.get("approved_competitors", None)

    if not industry or not market_segment:
        return jsonify({
            "status": "error",
            "message": "Both Industry and Market Segment inputs are required."
        }), 400

    data = generate_market_data(industry, market_segment, custom_providers)
    return jsonify(data)

@app.route("/api/reset", methods=["POST"])
def reset():
    global analysis_cache
    analysis_cache.clear()
    resp = jsonify({
        "status": "success",
        "message": "Cache and session state successfully reset."
    })
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

