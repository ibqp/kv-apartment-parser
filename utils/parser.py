import logging
from lxml import html
from config import xpaths
from typing import Optional, List
from requests.adapters import Response


class Parser:
    @staticmethod
    def parse_response(response: Response) -> Optional[html.HtmlElement]:
        try:
            logging.debug(f"Parsing HTML from received response. Response URL: {response.url}")
            decoded_content = response.content.decode('utf-8', errors='ignore')
            parsed_html = html.fromstring(decoded_content)
            if len(parsed_html) == 0:
                logging.error("Parsed HTML is empty.")
                return None

            logging.debug("HTML parsed successfully.")
            return parsed_html
        except Exception as e:
            logging.error(f"Failed to parse HTML: {e}")
            return None

    @staticmethod
    def extract_element(element: html.HtmlElement, xpath: str) -> Optional[List[str]]:
        try:
            logging.debug(f"Extracting elements using xpath: {xpath}")
            result = element.xpath(xpath)
            if not result:
                logging.debug("No elements found.")
                return None

            logging.debug("Elements extracted successfully.")
            return [str(item).strip() for item in result]
        except Exception as e:
            logging.error(f"Failed to extract elements: {e}")
            return None

    @staticmethod
    def extract_apartment_data(html, url):
        # Initialize data dictionary
        data = {
            'apurl': url

            # _parse_address
            , 'raw_address': None
            , 'street': None
            , 'district': None
            , 'subdistrict': None
            , 'city': None
            , 'parish': None

            # _parse_price
            , 'price': None

            # _parse_price_per_m2
            , 'price_per_m2': None

            # _parse_images
            , 'images': []

            # _parse_table_fields
            , 'rooms': None
            , 'bedrooms': None
            , 'total_area': None
            , 'floor': None
            , 'built_year': None
            , 'cadastre_no': None
            , 'energy_mark': None
            , 'utilities_summer': None
            , 'utilities_winter': None
            , 'ownership_form': None
            , 'condition': None
        }

        # Populate data dictionary wit parsed data
        Parser._parse_address(html, data)
        Parser._parse_price(html, data)
        Parser._parse_price_per_m2(html, data)
        Parser._parse_images(html, data)
        Parser._parse_table_fields(html, data)

        return data

    @staticmethod
    def _parse_address(html, data):
        address = Parser.extract_element(html, xpaths.APARTMENT_ADDRESS)
        if not address:
            logging.debug("Address not found. All address fields remain None.")
            return

        # example of default parsed address: 'apartment for sale - street, distinct, city...'
        address_parts = address[0].split(" - ")
        if len(address_parts) <= 1:
            logging.error("Check address format, something has changed. Expecting two parts but received only one. All address fields remain None.")
            return

        full_address = address_parts[1] # example: 'street, distinct, city...'
        data['raw_address'] = full_address # fill data dictionary with raw_address
        splitted_full_address = [part.strip() for part in full_address.split(",")] # example: ['street', 'distinct', 'city', ...]
        num_parts = len(splitted_full_address)

        # Define component mappings based on number of parts
        address_components = {
            4: {
                'street': 0
                , 'district': 1
                , 'city': 2
                , 'parish': 3
            }
            , 5: {
                'street': 0
                , 'subdistrict': 1  # sometimes full_address can have also a subdistrict
                , 'district': 2
                , 'city': 3
                , 'parish': 4
            }
        }

        # Get appropriate mapping
        if num_parts not in address_components:
            logging.debug(f"Address contains {num_parts} parts, expected 4 or 5. Address fields remains None (except raw_address).")
            return

        # Fill data dictionary with address components based on selected mapping
        selected_mapping = address_components[num_parts]
        for key, value in selected_mapping.items():
            data[key] = splitted_full_address[value]

    @staticmethod
    def _parse_price(html, data):
        price = Parser.extract_element(html, xpaths.APARTMENT_PRICE)
        if not price:
            logging.debug("Price not found. Field remains None.")
            return

        try:
            data['price'] = int(price[0].replace('\xa0', '').replace('€',''))
        except Exception as e:
            logging.error(f"Error parsing price: {e}")

    @staticmethod
    def _parse_price_per_m2(html, data):
        price_per_m2 = Parser.extract_element(html, xpaths.APARTMENT_PRICE_PER_M2)
        if not price_per_m2:
            logging.debug("Price per m2 not found. Field remains None.")
            return

        try:
            data['price_per_m2'] = int(price_per_m2[0].replace('\xa0', '').replace('€/m²',''))
        except Exception as e:
            logging.error(f"Error parsing price per m2: {e}")

    @staticmethod
    def _parse_images(html, data):
        images = Parser.extract_element(html, xpaths.APARTMENT_IMAGES)
        if not images:
            logging.debug("Images not found. Fields remains as empty list.")
            return
        data['images'] = images

    @staticmethod
    def _parse_table_fields(html, data):
        fields = {
            "rooms": xpaths.APARTMENT_ROOMS,
            "bedrooms": xpaths.APARTMENT_BEDROOMS,
            "total_area": xpaths.APARTMENT_TOTAL_AREA,
            "floor": xpaths.APARTMENT_FLOOR,
            "built_year": xpaths.APARTMENT_BUILD_YEAR,
            "cadastre_no": xpaths.APARTMENT_CADASTRE_NR,
            "energy_mark": xpaths.APARTMENT_ENERGY_MARK,
            "utilities_summer": xpaths.APARTMENT_UTILITIES_SUMMER,
            "utilities_winter": xpaths.APARTMENT_UTILITIES_WINTER,
            "ownership_form": xpaths.APARTMENT_OWNERSHIP_FORM,
            "condition": xpaths.APARTMENT_CONDITION
        }

        for field_name, xpath in fields.items():
            result = Parser.extract_element(html, xpath)
            if not result:
                logging.debug(f"{field_name} not found. Field remains None.")
                continue # move to next field

            try:
                if field_name == 'total_area':
                    data[field_name] = result[0].replace("m²", "").strip()
                elif field_name in ['utilities_summer', 'utilities_winter']:
                    data[field_name] = result[0].replace("€", "").strip()
                else:
                    data[field_name] = ", ".join(result)
            except Exception as e:
                logging.warning(f"Error parsing field {field_name}: {e}")
