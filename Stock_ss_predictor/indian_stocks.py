"""
This file contains the top 100 Indian stocks and their BSE/NSE symbols
"""

INDIAN_STOCKS = {
    # Nifty 50 Companies
    'Reliance Industries': 'RELIANCE.BSE',
    'Tata Consultancy Services': 'TCS.BSE',
    'HDFC Bank': 'HDFCBANK.BSE',
    'Infosys': 'INFY.BSE',
    'Hindustan Unilever': 'HINDUNILVR.BSE',
    'ICICI Bank': 'ICICIBANK.BSE',
    'State Bank of India': 'SBIN.BSE',
    'Bharti Airtel': 'BHARTIARTL.BSE',
    'ITC': 'ITC.BSE',
    'Kotak Mahindra Bank': 'KOTAKBANK.BSE',
    'Larsen & Toubro': 'LT.BSE',
    'Axis Bank': 'AXISBANK.BSE',
    'Asian Paints': 'ASIANPAINT.BSE',
    'HCL Technologies': 'HCLTECH.BSE',
    'Maruti Suzuki': 'MARUTI.BSE',
    'Bajaj Finance': 'BAJFINANCE.BSE',
    'Sun Pharmaceutical': 'SUNPHARMA.BSE',
    'Titan Company': 'TITAN.BSE',
    'UltraTech Cement': 'ULTRACEMCO.BSE',
    'Nestle India': 'NESTLEIND.BSE',
    
    # Additional Large Cap Companies
    'Power Grid Corporation': 'POWERGRID.BSE',
    'NTPC': 'NTPC.BSE',
    'Tata Motors': 'TATAMOTORS.BSE',
    'Adani Ports': 'ADANIPORTS.BSE',
    'Wipro': 'WIPRO.BSE',
    'Coal India': 'COALINDIA.BSE',
    'Indian Oil Corporation': 'IOC.BSE',
    'ONGC': 'ONGC.BSE',
    'JSW Steel': 'JSWSTEEL.BSE',
    'Grasim Industries': 'GRASIM.BSE',
    
    # Banking and Financial Services
    'HDFC Life Insurance': 'HDFCLIFE.BSE',
    'SBI Life Insurance': 'SBILIFE.BSE',
    'Bajaj Finserv': 'BAJAJFINSV.BSE',
    'ICICI Prudential Life': 'ICICIPRULI.BSE',
    'ICICI Lombard': 'ICICIGI.BSE',
    'Axis Bank': 'AXISBANK.BSE',
    'IndusInd Bank': 'INDUSINDBK.BSE',
    'Yes Bank': 'YESBANK.BSE',
    'Punjab National Bank': 'PNB.BSE',
    'Bank of Baroda': 'BANKBARODA.BSE',
    
    # IT and Technology
    'Tech Mahindra': 'TECHM.BSE',
    'MindTree': 'MINDTREE.BSE',
    'L&T Infotech': 'LTI.BSE',
    'Mphasis': 'MPHASIS.BSE',
    'Oracle Financial Services': 'OFSS.BSE',
    'Info Edge': 'NAUKRI.BSE',
    'Just Dial': 'JUSTDIAL.BSE',
    'Tata Elxsi': 'TATAELXSI.BSE',
    'NIIT Technologies': 'COFORGE.BSE',
    'Persistent Systems': 'PERSISTENT.BSE',
    
    # Pharmaceutical and Healthcare
    'Dr Reddy\'s Laboratories': 'DRREDDY.BSE',
    'Cipla': 'CIPLA.BSE',
    'Divi\'s Laboratories': 'DIVISLAB.BSE',
    'Aurobindo Pharma': 'AUROPHARMA.BSE',
    'Biocon': 'BIOCON.BSE',
    'Lupin': 'LUPIN.BSE',
    'Torrent Pharmaceuticals': 'TORNTPHARM.BSE',
    'Alkem Laboratories': 'ALKEM.BSE',
    'Ipca Laboratories': 'IPCALAB.BSE',
    'Glenmark Pharmaceuticals': 'GLENMARK.BSE',
    
    # Automobile and Auto Components
    'Mahindra & Mahindra': 'M&M.BSE',
    'Tata Motors': 'TATAMOTORS.BSE',
    'Hero MotoCorp': 'HEROMOTOCO.BSE',
    'Bajaj Auto': 'BAJAJ-AUTO.BSE',
    'Eicher Motors': 'EICHERMOT.BSE',
    'TVS Motor': 'TVSMOTOR.BSE',
    'Ashok Leyland': 'ASHOKLEY.BSE',
    'Motherson Sumi Systems': 'MOTHERSUMI.BSE',
    'Bosch': 'BOSCHLTD.BSE',
    'MRF': 'MRF.BSE',
    
    # Consumer Goods
    'Britannia Industries': 'BRITANNIA.BSE',
    'Dabur India': 'DABUR.BSE',
    'Marico': 'MARICO.BSE',
    'Godrej Consumer Products': 'GODREJCP.BSE',
    'Colgate-Palmolive': 'COLPAL.BSE',
    'United Spirits': 'MCDOWELL-N.BSE',
    'United Breweries': 'UBL.BSE',
    'Varun Beverages': 'VBL.BSE',
    'Tata Consumer Products': 'TATACONSUM.BSE',
    'Emami': 'EMAMILTD.BSE',
    
    # Infrastructure and Real Estate
    'DLF': 'DLF.BSE',
    'Godrej Properties': 'GODREJPROP.BSE',
    'Prestige Estates': 'PRESTIGE.BSE',
    'Phoenix Mills': 'PHOENIXLTD.BSE',
    'Brigade Enterprises': 'BRIGADE.BSE',
    'Oberoi Realty': 'OBEROIRLTY.BSE',
    'Sobha': 'SOBHA.BSE',
    'Indiabulls Real Estate': 'IBREALEST.BSE',
    'Sunteck Realty': 'SUNTECK.BSE',
    'Mahindra Lifespace': 'MAHLIFE.BSE',
    
    # Energy and Power
    'Adani Green Energy': 'ADANIGREEN.BSE',
    'Tata Power': 'TATAPOWER.BSE',
    'NHPC': 'NHPC.BSE',
    'Torrent Power': 'TORNTPOWER.BSE',
    'CESC': 'CESC.BSE',
    'JSW Energy': 'JSWENERGY.BSE',
    'Reliance Power': 'RPOWER.BSE',
    'Gujarat Gas': 'GUJGAS.BSE',
    'Indraprastha Gas': 'IGL.BSE',
    'Petronet LNG': 'PETRONET.BSE'
}

def get_stock_info(stock_name):
    """
    Get the BSE/NSE symbol for a given stock name
    """
    return INDIAN_STOCKS.get(stock_name)

def get_all_stocks():
    """
    Get a list of all available stock names
    """
    return list(INDIAN_STOCKS.keys())

def get_stocks_by_sector(sector):
    """
    Get stocks filtered by sector based on the dictionary structure
    Note: This is a basic implementation and can be enhanced with proper sector tagging
    """
    sectors = {
        'BANKING': ['HDFC Bank', 'ICICI Bank', 'State Bank of India', 'Kotak Mahindra Bank', 'Axis Bank'],
        'IT': ['Tata Consultancy Services', 'Infosys', 'HCL Technologies', 'Wipro', 'Tech Mahindra'],
        'PHARMA': ['Sun Pharmaceutical', 'Dr Reddy\'s Laboratories', 'Cipla', 'Divi\'s Laboratories', 'Biocon'],
        'AUTO': ['Maruti Suzuki', 'Mahindra & Mahindra', 'Tata Motors', 'Hero MotoCorp', 'Bajaj Auto'],
        'CONSUMER': ['Hindustan Unilever', 'ITC', 'Nestle India', 'Britannia Industries', 'Dabur India']
    }
    return sectors.get(sector.upper(), []) 