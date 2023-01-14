import re
import json
import asyncio
import tempfile
import platform
import webbrowser
from datetime import datetime

from pyppeteer import launch
from pyppeteer_stealth import stealth

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static

from rich.markdown import Markdown

MARKDOWN = """
# This is a Terminal App

## Knwon issues
- Image not showing in post
- URLs in post cannot be clicked

## 求助養
樓豬需要飼料，請餵食。捐助鏈接：
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

if platform.system() == 'Windows':
	input('Set "MS Gothic" as your font in CMD [如果你看到這句文字就可以按enter繼續了]\n\n')

class CategoryMenu(Static):
	def compose(self) -> ComposeResult:
		yield Button("吹水台", name="cat1")
		yield Button("創意台", name="cat31")
		yield Button("熱　門", name="cat2")
		yield Button("講故台", name="cat12")
		yield Button("最　新", name="cat3")
		yield Button("學術台", name="cat18")
		yield Button("時事台", name="cat5")
		yield Button("World", name="cat38")
		yield Button("政事台", name="cat33")
		yield Button("財經台", name="cat15")
		yield Button("娛樂台", name="cat7")
		yield Button("房屋台", name="cat37")
		yield Button("手機台", name="cat4")
		yield Button("硬件台", name="cat22")
		yield Button("Apps台", name="cat9")
		yield Button("軟件台", name="cat26")
		yield Button("電訊台", name="cat35")
		yield Button("創意台", name="cat31")
		yield Button("健康台", name="cat36")
		yield Button("飲食台", name="cat16")
		yield Button("感情台", name="cat30")
		yield Button("旅遊台", name="cat17")
		yield Button("上班台", name="cat14")
		yield Button("活動台", name="cat27")
		yield Button("校園台", name="cat19")
		yield Button("體育台", name="cat6")
		yield Button("學術台", name="cat18")
		yield Button("講故台", name="cat12")
		yield Button("遊戲台", name="cat10")
		yield Button("影視台", name="cat11")
		yield Button("動漫台", name="cat8")
		yield Button("攝影台", name="cat23")
		yield Button("音樂台", name="cat21")
		yield Button("汽車台", name="cat20")
		yield Button("寵物台", name="cat25")
		yield Button("潮流台", name="cat13")
		yield Button("玩具台", name="cat24")
		yield Button("直播台", name="cat34")
		yield Button("站務台", name="cat28")
		yield Button("黑　洞", name="cat32")


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

	CSS = '''
	Screen {
		 layout: horizontal;
	}

	Post {
		 margin: 1 0;
		 width: 100%;
		 align: left top;
		 content-align: left top;
	}

	Post Button {
		 background: $boost;
		 width: 100%;
		 height: auto;
		 border: none;
		 align: left top;
		 content-align: left top;
	}

	CategoryMenu {
		 layout: grid;
		 grid-size: 4 10;
	}

	#leftpanel {
		 width: 30%;
	}

	#rightpanel {
		 width: 70%;
	}

	.noshow {
		visibility: hidden;
		display: none;
	}
	'''

	BINDINGS = [
		("d", "toggle_dark", "Toggle dark mode"),
		("q", "quit", "Quit LIHKGApp"),
		("s", "switch_channel", "Switch Channel"),
		("n", "download_next_page", "load Next page"),
		("m", "download_more_post", "load More post"),
	]

	def on_mount(self):
		self.loaded_page = 0
		self.total_page = 0
		self.action_download_more_post()

	def parse_post_response(self, json_dict):
		a = re.compile(r'" data-sr-url=".*?">')
		i = re.compile(r'" data-thumbnail-src=.*? />')
		e = re.compile(r'" class=.*? />')
		s = re.compile(r'<span.*?>')
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
			msg = i.sub(')\n\n', msg)
			msg = e.sub(')\n\n', msg)
			msg = msg.replace('<img src="', '\n\n> ![](')
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
		if button_id == "read":
			self.thread_id = event.button.name
			self.loaded_page = 1
			self.post_md = ''
			self.total_page = 0
			asyncio.create_task(
				self.get_post_content(self.thread_id,
									  self.loaded_page))
			self.query_one('CategoryMenu').add_class("noshow")
		elif "cat" in event.button.name:
			for post in self.query("Post"):
				post.remove()
			asyncio.create_task(self.get_post_list(
				event.button.name[3:]))

	def compose(self) -> ComposeResult:
		"""Called to add widgets to the app."""
		yield Header()
		yield Footer()
		yield Container(id="leftpanel")
		yield Container(CategoryMenu(), Static(README, id="post"), id="rightpanel")

	def add_post(self, json_dict) -> None:
		"""An action to add a post."""
		new_post = Post(json_dict)
		self.query_one("#leftpanel").mount(new_post)

	def action_toggle_dark(self) -> None:
		"""An action to toggle dark mode."""
		self.dark = not self.dark

	def action_download_next_page(self) -> None:
		if self.loaded_page < self.total_page:
			self.post_md += f' Page {self.loaded_page} End'
			self.post_md += '\n\n---\n\n'
			self.loaded_page += 1
			asyncio.create_task(
				self.get_post_content(self.thread_id,
									  self.loaded_page))

	def action_download_more_post(self) -> None:
		asyncio.create_task(self.get_post_list())

	def action_switch_channel(self) -> None:
		menu = self.query_one('CategoryMenu')
		menu.remove_class("noshow")
		menu.scroll_visible()

	def webbrowser_open_url(self, url):
		webbrowser.open(url)

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
		if ('error_code' in self.data or
				'error_message' in self.data):
			self.query_one("#leftpanel").mount(
				Static(self.data['error_message']))
		else:
			for json_dict in self.data['response']['items']:
				self.add_post(json_dict)
		await asyncio.sleep(10)

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
		if self.loaded_page == 1:
			self.total_page = self.post_dict['response']['total_page']
		self.post_md += self.parse_post_response(self.post_dict)
		self.query_one("#post").update(Markdown(self.post_md))
		await asyncio.sleep(10)

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
