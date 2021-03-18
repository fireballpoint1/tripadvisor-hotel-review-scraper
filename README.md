# TripAdvisor Scrapper

Scrape the hotel reviews of a whole city on [TripAdvisor](http://www.tripadvisor.com).

## Requirements

- python 3.5

## Installation & Setup
Download and install required libs and data:
```bash
pip install bs4
```

## Usage Scrapper
Store all reviews of Hotel Pan Pacific Singapore:
```python
python3 tripadvisor-scrapper.py 294265 d302294 Pan_Pacific_Singapore-Singapore
```

The scrapper requires the `city location id`, `hotel id` and the ```hotel+city name``` as commandline arguments.
Both can be retrieved from the url, for example, `https://www.tripadvisor.com.sg/Hotel_Review-g294265-d302294-Reviews-Pan_Pacific_Singapore-Singapore.html`
The ```city location id``` is the number after the g. The `hotel id` is the number after d. The ```hotel+city name``` is the string from the dash after the Reviews to the dot before ```html```.

## Author
- updated by: [Mayank Modi](mailto:mayank.modi.iiit@gmail.com)
- source: [Michael Andorfer](mailto:mandorfer.mmt-b2014@fh-salzburg.ac.at)
