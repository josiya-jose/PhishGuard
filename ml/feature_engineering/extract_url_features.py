import re
import pandas as pd
from urllib.parse import urlparse


# ============================================
# URL NORMALIZATION (CRITICAL FIX)
# ============================================

def normalize_url(url: str) -> str:
    """
    Ensures URL always has scheme.
    Fixes issue where www.google.com breaks parsing.
    """
    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


# ============================================
# HELPER FUNCTIONS
# ============================================

def having_ip_address(url):
    return -1 if re.search(r"\d+\.\d+\.\d+\.\d+", url) else 1


def url_length(url):
    length = len(url)
    if length < 54:
        return 1
    elif 54 <= length <= 75:
        return 0
    else:
        return -1


def shortening_service(url):
    services = ["bit.ly", "tinyurl", "goo.gl", "ow.ly", "t.co"]
    return -1 if any(service in url for service in services) else 1


def having_at_symbol(url):
    return -1 if "@" in url else 1


def double_slash_redirecting(url):
    # ignore the first 'https://'
    return -1 if url.count("//") > 1 else 1


def prefix_suffix(domain):
    return -1 if "-" in domain else 1


def having_sub_domain(domain):
    dots = domain.count(".")
    if dots == 1:
        return 1
    elif dots == 2:
        return 0
    else:
        return -1


def https_token(domain):
    return -1 if "https" in domain else 1


# ============================================
# MAIN FEATURE EXTRACTION
# ============================================

def extract_features(url: str):

    # 🔥 Normalize first
    url = normalize_url(url)

    parsed = urlparse(url)
    domain = parsed.netloc

    features = {
        "having_IP_Address": having_ip_address(url),
        "URL_Length": url_length(url),
        "Shortining_Service": shortening_service(url),
        "having_At_Symbol": having_at_symbol(url),
        "double_slash_redirecting": double_slash_redirecting(url),
        "Prefix_Suffix": prefix_suffix(domain),
        "having_Sub_Domain": having_sub_domain(domain),
        "SSLfinal_State": 1 if parsed.scheme == "https" else -1,
        "Domain_registeration_length": 0,
        "Favicon": 0,
        "port": -1 if parsed.port else 1,
        "HTTPS_token": https_token(domain),
        "Request_URL": 0,
        "URL_of_Anchor": 0,
        "Links_in_tags": 0,
        "SFH": 0,
        "Submitting_to_email": 1,
        "Abnormal_URL": 1,
        "Redirect": 0,
        "on_mouseover": 1,
        "RightClick": 1,
        "popUpWidnow": 1,
        "Iframe": 1,
        "age_of_domain": 0,
        "DNSRecord": 0,
        "web_traffic": 0,
        "Page_Rank": 0,
        "Google_Index": 1,
        "Links_pointing_to_page": 0,
        "Statistical_report": 1,
    }

    return pd.DataFrame([features])