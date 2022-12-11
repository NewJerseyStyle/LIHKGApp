import re
import json
import asyncio
import tempfile
import platform
import webbrowser
from time import sleep
from datetime import datetime

from pyppeteer import launch
from pyppeteer_stealth import stealth
import nest_asyncio

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static

from rich.markdown import Markdown

MARKDOWN = """
# This is a Terminal App

Rich can do a pretty *decent* job of rendering markdown.

## Knwon issues
- Only threads in category 5 is showing
- Image not showing in post
- URLs in post cannot be clicked

## 求助養
樓豬需要飼料，請餵食金錢，讓金錢的味道鞭策樓豬快手修補以上問題。

捐助鏈接：
```python
'''
   ▄▄▄▄▄▄▄  ▄  ▄▄▄▄  ▄▄  ▄▄▄▄▄▄▄  
   █ ▄▄▄ █ █▄▄██ ▀▀ █▀▄▄ █ ▄▄▄ █  
   █ ███ █ ▄▀▀▀ ▄██▄ █▀  █ ███ █  
   █▄▄▄▄▄█ █▀▄▀▄▀▄▀▄ █▀█ █▄▄▄▄▄█  
   ▄▄ ▄  ▄▄▀▀▄ ▀▄█ ▀▀█▀▀ ▄▄▄ ▄▄   
    █████▄ ▄▄█▀ █▄▀█▄ ▄▀▀▀  █▄▄▀  
   ▀ █▀▄▀▄ ▄   ▄█ █ ▄ ▄▄██▀▀▄▀█▄  
   ▀█▀ ▄▀▄▄▀▀█▀█▄▀  ▀▄▀█▄▄▀ ▄▄▄▄  
   ▀▄ ██▄▄▀ ▄▀▄▀▀▀  █▀▄▄▄ ▄ ▀ █   
   ▄ ▀▀▄▄▄██    ▀▀ ██    ▀█ ▀ ▄█  
   ▄ █▀  ▄▀ ▀▄█▄▄█ ▀▀▀ ▄▄█▄▄ ▄▀▀  
   ▄▄▄▄▄▄▄ █▄ ██▀█ █  ▀█ ▄ █ ▀█▀  
   █ ▄▄▄ █  ▄▀█▀▀█▀█▄█ █▄▄▄█▀▀▀▀  
   █ ███ █ ▀▀▀█ █▄    █  ▀ ███▀▄  
   █▄▄▄▄▄█ ██▄▀▄▄ █▀█▀▀█▄▀▄█  █   
'''
```
"""

README = Markdown(MARKDOWN)
TEMP_PATH = tempfile.TemporaryDirectory()
nest_asyncio.apply()

if platform.system() == 'Windows':
	input('Set "MS Gothic" as your font in CMD [如果你看到這句文字就可以按enter繼續了]')

class Post(Static):
	def __init__(self, data):
		super(Post, self).__init__()
		self.thread_id = data["thread_id"]
		self.title = f'<{data["user_nickname"]}>'
		self.title += f' {data["like_count"] - data["dislike_count"]}'
		self.title += f' [{data["total_page"]}p] `{data["category"]["name"]}`\n\n'
		self.title += f'{data["title"]}'

	def compose(self) -> ComposeResult:
		yield Button(self.title, id="read", name=self.thread_id, variant="success")


class LIHKGApp(App):
	"""A Textual app to view LIHKG."""

	DEFAULT_CSS = '''
	Screen {
	    layout: horizontal;
	}

	Post {
	    margin: 1 0;
	}

	Button {
	    background: $boost;
	    width: 100%;
	    height: auto;
	    border: none;
	}


	#leftpanel {
	    width: 30%;
	}

	#rightpanel {
	    width: 70%;
	}
	'''

	BINDINGS = [
		("d", "toggle_dark", "Toggle dark mode"),
		("q", "quit", "Quit LIHKGApp"),
		# ("v", "view_full_screen", "View full page"),
		("n", "download_next_page", "load Next page"),
		("m", "download_more_post", "load More post"),
	]

	def on_mount(self):
		asyncio.get_event_loop().run_until_complete(
			self.get_post_list())
		for json_dict in self.data['response']['items']:
			self.add_post(json_dict)

	def parse_post_response(self, json_dict):
		a = re.compile(r'" data-sr-url=".*?">')
		i = re.compile(r'" data-thumbnail-src=.*? />')
		e = re.compile(r'" class=.*? />')
		s = re.compile(r'<span.*? >')
		post_md = ''
		for post in json_dict['response']['item_data']:
			post_md += f'\#{post["msg_num"]} <{post["user_nickname"]}> '
			post_md +=f'[{datetime.fromtimestamp(post["reply_time"])}]\n\n'
			msg = post['msg']
			msg = msg.replace('<strong>', '*')
			msg = msg.replace('</strong>', '*')
			msg = msg.replace('<br />', '\n\n')
			msg = s.sub('`', msg)
			msg = msg.replace('</span>', '`')
			msg = i.sub(')', msg)
			msg = e.sub(')', msg)
			msg = msg.replace('<img src="', '> ![](')
			msg = msg.replace('<a href="', '[')
			msg = a.sub('](', msg)
			msg = msg.replace('</a>', ')')
			while '![](' in msg:
				url = msg.split('![](')[1].split(')')[0]
				msg = msg.replace('![](', f'![{url}](')
			post_md += msg
			post_md += '\n\n---\n\n'
		return post_md

	def on_button_pressed(self, event: Button.Pressed) -> None:
		"""Event handler called when a button is pressed."""
		button_id = event.button.id
		thread_id = event.button.name
		post_display = self.query_one("#post")
		if button_id == "read":
			self.loaded_page = 1
			asyncio.get_event_loop().run_until_complete(
				self.get_post_content(thread_id, self.loaded_page))
			self.post_md = self.parse_post_response(self.post_dict)
			post_display.update(Markdown(self.post_md))

	def compose(self) -> ComposeResult:
		"""Called to add widgets to the app."""
		yield Header()
		yield Footer()
		yield Container(id="leftpanel")
		yield Container(Static(README, id="post"), id="rightpanel")

	def add_post(self, json_dict) -> None:
		"""An action to add a post."""
		new_post = Post(json_dict)
		self.query_one("#leftpanel").mount(new_post)

	def action_toggle_dark(self) -> None:
		"""An action to toggle dark mode."""
		self.dark = not self.dark

	def action_download_next_page(self) -> None:
		if self.loaded_page < self.post_dict['total_page']:
			self.post_md += f' Page {self.loaded_page} End'
			self.post_md += '\n\n---\n\n'
			asyncio.get_event_loop().run_until_complete(
				self.get_post_content(thread_id, self.loaded_page))
			self.post_md += self.parse_post_response(self.post_dict)
			post_display.update(Markdown(self.post_md))
			self.loaded_page += 1

	def action_download_more_post(self) -> None:
		asyncio.get_event_loop().run_until_complete(
			self.get_post_list())
		if self.data['error_code'] == 100:
			self.query_one("#leftpanel").mount(
				Static(self.data['error_message']))
		else:
			for json_dict in self.data['response']['items']:
				self.add_post(json_dict)

	def webbrowser_open_url(self, url):
		webbrowser.open(url)

	# def on_container_mousescrolldown(self, message):
	# 	post_display = self.query_one("#post")
	# 	if (message.y - post_display.styles.height < self.styles.height
	# 		and self.loaded_page < self.post_dict['total_page']):
	# 		self.action_download_nextpage()

	async def get_post_list(self, cat='5'):
		browser = await launch(headless=True,
								userDataDir=TEMP_PATH.name,
								args=['--no-sandbox'])
		page = await browser.newPage()
		await stealth(page)
		page.on('response',
			lambda res: asyncio.ensure_future(
				self.interception_cat(res, cat)))
		await page.goto(f'https://lihkg.com/category/{cat}',
						{'waitUntil': 'networkidle2'})
		await page.close()
		await browser.close()
		await asyncio.sleep(5)

	async def interception_cat(self, response, cat):
		# Response logic goes here
		if ('https://lihkg.com/api_v2/thread' +
			f'/category?cat_id={cat}&page=' in response.url):
			self.data = await response.json()

	async def get_post_content(self, thread_id, page_num):
		browser = await launch(headless=True,
								userDataDir=TEMP_PATH.name,
								args=['--no-sandbox'])
		page = await browser.newPage()
		await stealth(page)
		page.on('response',
			lambda res: asyncio.ensure_future(
				self.interception_thread(res,
										 thread_id,
										 page_num)))
		await page.goto(f'https://lihkg.com/thread/{thread_id}' +
						f'/page/{page_num}',
						{'waitUntil': 'networkidle2'})
		await page.close()
		await browser.close()
		await asyncio.sleep(5)

	async def interception_thread(self, response, thread_id, page_num):
		# Response logic goes here
		if (f'https://lihkg.com/api_v2/thread/{thread_id}' +
			f'/page/{page_num}' in response.url):
			self.post_dict = await response.json()

if __name__ == "__main__":
	app = LIHKGApp()
	app.run()
	asyncio.get_event_loop().close()
	TEMP_PATH.cleanup()
