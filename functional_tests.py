from selenium import webdriver

browser = webdriver.Firefox()
browser.get('http://localhost:8000')

# Check that the web page contains 'Django'
assert 'Django' in browser.title

