from datetime import datetime
import csv
import re
import time
import requests
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie

class KinopoiskScraper:
    """
    A class for scraping user ratings from Kinopoisk.ru.
    
    This scraper extracts a user's movie and TV show ratings from their Kinopoisk profile,
    including titles (in Russian and English), ratings, year, duration, and other metadata.
    Authentication is handled using cookies from a logged-in session.
    """
    def __init__(self, user_id, cookies_string):
        """
        Initialize the scraper with user credentials.
        
        Args:
            user_id (str): The Kinopoisk user ID to scrape ratings from
            cookies_string (str): Authentication cookies from a logged-in browser session
        """
        self.user_id = user_id
        self.cookies = self._format_cookies(cookies_string)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Referer': f"https://www.kinopoisk.ru/user/{user_id}/votes/"
        }
        
    def _format_cookies(self, raw_cookies):
        """
        Convert raw cookie string into a dictionary format for requests.
        
        Args:
            raw_cookies (str): Raw cookie string from browser
            
        Returns:
            dict: Formatted cookies dictionary
        """
        cookie = SimpleCookie()
        cookie.load(raw_cookies)
        return {key: morsel.value for key, morsel in cookie.items()}
    
    def get_total_pages(self):
        """
        Determine the total number of pages of ratings to scrape.
        
        Kinopoisk displays 50 ratings per page, so this calculates the total
        number of pages based on the total number of ratings.
        
        Returns:
            int: Number of pages to scrape
        """
        url = f"https://www.kinopoisk.ru/user/{self.user_id}/votes/list/vs/vote/page/1/#list"
        print(f"Fetching total pages info from: {url}")
        
        try:
            response = requests.get(url, cookies=self.cookies, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for pagination info
            pages_from_to_div = soup.find("div", class_="pagesFromTo")
            if pages_from_to_div:
                # Format: "1–50 из 458"
                match = re.search(r'из\s*(\d+)', pages_from_to_div.text)
                if match:
                    total_ratings = int(match.group(1))
                    print(f"Found total ratings: {total_ratings}")
                    return (total_ratings + 49) // 50  # 50 items per page, ceiling division
            
            # Alternative: Check for profile votes total
            total_span = soup.find("span", class_="profile_V2_votes_total")
            if total_span:
                match = re.search(r'(\d+)', total_span.text)
                if match:
                    total_ratings = int(match.group(1))
                    print(f"Found total ratings: {total_ratings}")
                    return (total_ratings + 49) // 50
            
            # If we can't determine, assume there's at least one page
            print("Could not determine total pages. Assuming 1 page.")
            return 1
            
        except Exception as e:
            print(f"Error fetching total pages: {e}")
            return 0
    
    def fetch_ratings_page(self, page_num):
        """
        Fetch a specific page of ratings from Kinopoisk.
        
        Args:
            page_num (int): Page number to fetch
            
        Returns:
            list: BeautifulSoup elements representing rating items
        """
        url = f"https://www.kinopoisk.ru/user/{self.user_id}/votes/list/vs/vote/page/{page_num}/#list"
        print(f"Fetching page {page_num}: {url}")
        
        try:
            response = requests.get(url, cookies=self.cookies, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all movie/show items
            items = soup.find_all("div", class_="item")
            return items
            
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            return []
    
    def parse_rating_item(self, item):
        """
        Extract details from a single rating item HTML element.
        
        Parses title, rating, year, type, duration and rating date from the HTML.
        
        Args:
            item (BeautifulSoup element): HTML element containing rating information
            
        Returns:
            dict: Dictionary with extracted information
        """
        result = {
            "num": "",
            "nameRus": "",
            "nameEng": "",
            "rating": "",
            "year": "",
            "type": "",
            "duration": "",
            "date_rated": ""
        }
        
        try:
            # Extract item number
            num_div = item.find("div", class_="num")
            if num_div:
                result["num"] = num_div.text.strip()
            
            # Extract Russian name and year
            name_rus_link = item.select_one("div.nameRus a")
            if name_rus_link:
                full_name_text = name_rus_link.text.strip()
                # Check if it has year in parentheses: "Movie Name (2021)"
                match = re.match(r"^(.*?)\s*\((\d{4})\)$", full_name_text)
                if match:
                    result["nameRus"] = match.group(1).strip()
                    result["year"] = match.group(2)
                else:
                    result["nameRus"] = full_name_text
            
            # Extract English name
            name_eng_div = item.find("div", class_="nameEng")
            if name_eng_div:
                result["nameEng"] = name_eng_div.text.strip()
                # Check if it's just a non-breaking space
                if result["nameEng"] == '\xa0':
                    result["nameEng"] = ""
            
            # Rating extraction - multiple approaches to handle different HTML structures
            vote_widget = item.find("div", class_="vote_widget")
            if vote_widget:
                # Look for a div that has both classes containing "show_vote_" AND "myVote"
                my_vote_divs = vote_widget.find_all("div")
                for div in my_vote_divs:
                    if div.has_attr("class"):
                        class_str = " ".join(div["class"])
                        if "myVote" in class_str and "show_vote_" in class_str:
                            result["rating"] = div.text.strip()
                            break
                
                # If still not found, try another approach - looking directly in the script tag
                if not result["rating"]:
                    script_tags = item.find_all("script")
                    for script in script_tags:
                        if script.string and "rating:" in script.string:
                            # Extract rating from: ur_data.push({film: 935940, rating: '7', ...
                            rating_match = re.search(r"rating:\s*'(\d+)'", script.string)
                            if rating_match:
                                result["rating"] = rating_match.group(1)
                                break
            
            # If rating is still empty, try one more approach
            if not result["rating"]:
                # Look for div with attribute vote
                rate_now_div = item.select_one("div.rateNow[vote]")
                if rate_now_div and rate_now_div.has_attr("vote"):
                    result["rating"] = rate_now_div["vote"]
            
            # Extract duration
            rating_div = item.find("div", class_="rating")
            if rating_div:
                duration_span = rating_div.find("span", class_="text-grey", string=re.compile(r'\d+\s*мин\.?'))
                if duration_span:
                    match = re.search(r'(\d+)', duration_span.text)
                    if match:
                        result["duration"] = match.group(1)
            
            # Extract content type (film/series)
            type_div = item.select_one("div[class*='MyKP_Folder_Select_'][type]")
            if type_div and type_div.has_attr('type'):
                result["type"] = type_div['type']
            else:
                # Default to "film" if not specified
                result["type"] = "film"
            
            # Extract date rated
            date_div = item.find("div", class_="date")
            if date_div:
                date_str = date_div.text.strip()
                try:
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y, %H:%M")
                    result["date_rated"] = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    result["date_rated"] = date_str
            
            return result
            
        except Exception as e:
            print(f"Error parsing item #{result['num']}: {e}")
            return result
    
    def extract_from_html(self, html_content):
        """
        Extract ratings from raw HTML content (useful for testing).
        
        Args:
            html_content (str): Raw HTML content to parse
            
        Returns:
            list: List of dictionaries containing rating data
        """
        soup = BeautifulSoup(html_content, "html.parser")
        items = soup.find_all("div", class_="item")
        results = []
        
        for item in items:
            rating_data = self.parse_rating_item(item)
            if rating_data["nameRus"] or rating_data["nameEng"]:
                results.append(rating_data)
                
        return results
    
    def export_to_csv(self, filename="kinopoisk_ratings.csv"):
        """
        Export all ratings to CSV file.
        
        This method:
        1. Determines total number of rating pages
        2. Scrapes each page
        3. Extracts all movie/show details
        4. Saves the data to a CSV file
        
        Args:
            filename (str): Path to save the CSV file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        total_pages = self.get_total_pages()
        if total_pages == 0:
            print("Could not determine the number of pages. Exiting.")
            return False
        
        print(f"Found {total_pages} pages of ratings to process.")
        all_ratings = []
        
        for page in range(1, total_pages + 1):
            items = self.fetch_ratings_page(page)
            if not items:
                print(f"No items found on page {page}.")
                continue
                
            print(f"Processing {len(items)} items from page {page}...")
            for item in items:
                rating_data = self.parse_rating_item(item)
                if rating_data["nameRus"] or rating_data["nameEng"]:  # Only add if we got a name
                    all_ratings.append(rating_data)
                    
                    # Debug: Print each extracted rating
                    print(f"Item #{rating_data['num']}: {rating_data['nameRus']} - Rating: {rating_data['rating']}")
            
            # Sleep to avoid rate limiting
            if page < total_pages:
                print("Waiting before fetching next page...")
                time.sleep(1.5)
        
        # Write to CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["num", "nameRus", "nameEng", "rating", "year", 
                             "type", "duration", "date_rated"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for rating in all_ratings:
                    writer.writerow(rating)
                
            print(f"Successfully exported {len(all_ratings)} ratings to {filename}")
            return True
        
        except Exception as e:
            print(f"Error writing to CSV: {e}")
            return False


def main():
    """
    Main function to demonstrate scraper usage.
    
    Loads credentials from cookies_file.py or uses default values,
    then runs the scraper to extract and export ratings.
    """
    # You would normally import these from a config file
    try:
        from cookies_file import cookies as KINOPOISK_COOKIES, number_user as KINOPOISK_USER_ID
        print(f"Loaded user ID and cookies from cookies_file.py")
    except ImportError:
        print("cookies_file.py not found. Using values from script.")
        # Replace these with your actual values if not using cookies_file.py
        KINOPOISK_USER_ID = "your_user_id_here"
        KINOPOISK_COOKIES = "your_cookies_string_here"

    start_time = time.time()
    scraper = KinopoiskScraper(KINOPOISK_USER_ID, KINOPOISK_COOKIES)
    scraper.export_to_csv()
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()