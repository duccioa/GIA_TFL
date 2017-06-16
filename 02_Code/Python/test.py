from lxml import html

s = '''<div class="my_div">    <a href="/foobar">        <img src="my_img.png">    </a></div>'''

tree = html.fromstring(s)
# when you do path... //a, you are ALREADY at 'a' node
for el in tree.xpath('//div[contains(@class, "pos-rel")]//a'):
    # you were trying to get next children /@href, which doesn't exist
    print(el.xpath('@href')) # you should instead access the existing node's
    print(el.xpath('img/@src')) # same here, not /img/@src ...

['/foobar']
['my_img.png']