from bs4 import BeautifulSoup
import pandas as pd
import requests


class WebScrap:
    _headers = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/122.0.0.0 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})

    def __init__(self):
        url = self._url_to_web_scrap('https://www.mwcbarcelona.com/agenda/speakers')
        links = self._get_speaker_link(url)
        speakers = self._speaker_data(links)
        self.save_data_in_a_csv_file(speakers)

    def _url_to_web_scrap(self, url):
        """
        param url for the site to web scrap: :return content of HTML, if the website was no accessed successfully the
        function will return now. Will stop the program from executing any further processes:
        """
        # Making a GET request
        r = requests.get(url, headers=self._headers)
        # check status code for response received
        # success code - 200
        if r.status_code == 200:
            # Parsing the HTML
            return BeautifulSoup(r.content, 'lxml')
        return None

    def _get_speaker_link(self, html_content):
        """
        This function gets all the links for the speakers.
        The links will then be used to extract data about speakers and events
        :param html_content:
        :return:
        :param html_content this the html content return by _url_to_web_scrap:
        :return list of links of the speaker pages:
        """
        _speaker_link = 'https://www.mwcbarcelona.com'
        _links = list()
        result = html_content.find_all(class_='speaker-card')
        # Extract content from each speaker card
        if result is not None:
            for card in result:
                try:
                    # Extract link
                    _link = _speaker_link + card['href']
                    _links.append(_link)
                except:
                    None

            # return list of links
            return _links
        return None

    def _find_speaker_details(self, soup):
        _speaker_name = soup.find('h1').text.strip()
        _position_company = soup.find('h3').text.strip()
        i = _position_company.rindex(',')  # Last index of the comma to get company name
        company_name = _position_company[i + 1:]
        position = _position_company[:i].replace(',', ';')

        return _speaker_name + ', ' + position + ', ' + company_name

    def _find_linkedin_profile(self, search_string):

        # search google for speakers LinkedIn profile
        _soup = self._url_to_web_scrap('https://www.google.com/search?q=' + search_string)
        if _soup is not None:
            # find LinkedIn profile from the tags
            _linkedin_link = _soup.find('a', href=lambda href: href and 'linkedin.com/in/' in href)
            if _linkedin_link:
                # if LinkedIn profile is found, return it, else return None
                return _linkedin_link['href']

        return None


    def _find_event_and_location(self, soup):

        _links = [a['href'] for a in soup.select('aside a')]
        _events = list()
        _locations = list()
        _dates = list()
        _event_link = 'https://www.mwcbarcelona.com'
        for url in _links:
            soup = self._url_to_web_scrap(_event_link + url)
            try:
                # Extracting Conference Name
                _conference_name = soup.find('h1').text.strip()
                # Extracting When
                _when_div = soup.find('div', id='when')
                _when = _when_div.find_all('p')[0].text.strip()

                # Extracting Location
                _location_div = soup.find('div', id='location')
                _location = _location_div.find('p').text.strip()

            except:
                None
            _events.append(_conference_name)
            _locations.append(_location)
            _dates.append(_when)

        return zip(_events, _locations, _dates)

    def _speaker_data(self, links):

        count = 0
        _speakers = list()
        # Extract content from each speaker card
        if links:

            for link in links:
                try:
                    soup = self._url_to_web_scrap(link)
                    # get name, position and company name
                    _speaker_details = self._find_speaker_details(soup)
                    _search_string = _speaker_details.replace(',', ' ')
                    # get LinkedIn profile
                    _linkedin_profile = self._find_linkedin_profile(_search_string)
                    # get events and location
                    _event_and_location = self._find_event_and_location(soup)

                    for event_a in _event_and_location:
                        if _linkedin_profile is not None:
                            full_details = _speaker_details + ',' + _linkedin_profile + ',' + event_a[0].replace(',',
                                                                                                                 ';') + \
                                           ', ' + event_a[1] + ',' + event_a[2]
                        else:
                            full_details = _speaker_details + ',' + 'No linkedIn' + ',' + event_a[0].replace(',', ';') + \
                                           ', ' + event_a[1] + ',' + event_a[2]
                        print(full_details)

                    _speakers.append(full_details.split(','))
                except:
                    None

        return _speakers

    def save_data_in_a_csv_file(self, full_details):

        data = pd.DataFrame.from_records(full_details,
                                         columns=['Name', 'Position', 'Company', 'Linkedin_Profile', 'Conference',
                                                  'Conference_location',
                                                  'Hall', 'Day', 'Unknown'])
        # for testing purposes, name and position is used as primary key
        # data.set_index(['Names', 'Positions','Company'], inplace=True)
        # add data to a csv file
        data.to_csv('speakers_20240411.csv', encoding='utf-8')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    web = WebScrap()
