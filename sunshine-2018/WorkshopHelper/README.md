WorkshopHelper
==============

We're given the URL to a webpage. Once there, we're asked to help out
at the workshop. The page gives us a clue about which problem to
solve and then expects us to solve. We're only given ten seconds to
discourage us from being able to do them by hand.

So let's take a quick glance at the source to see what we're dealing
with here... Surprise! All the important stuff is generated somehow
at runtime using Javascript.

So that pretty much rules out using Python or a similar scripting
language to fetch and parse the HTML and submit a solution. No sense
wading through all that minimized Javascript to figure out what's
going on.

Instead we'll use
[Puppeteer](https://github.com/GoogleChrome/puppeteer), a Node API
for headless Chrome. Using the API, we can use Javascript to control
and automate a Chrome instance. The API is pretty flexible: we can
explore the DOM of a webpage, simulate user action, save screenshots
of pages, and more.

We can break the task up into several parts:

1. Launch headless Chrome, navigate to the page, and press Start on
the welcome page. We give the page 1 second to respond and load the
first puzzle page. The code below will open up a visible window and
wait 20 milliseconds between each action so that you can watch what's
happening. You can also just let it run at fullspeed without
displaying anything by removing the `headless` and `slowMo`
arguments. Puppeteer has a `$` method similar to jQuery's `$` method
or the more modern `document.querySelector` that allows us to select
an element on the page. Once we have an handle to the element,
Puppeteer provides a `click` method to simulate user input. Note that
this code all executes in the Node environment and not the Chrome
instance's web environment. Calling `click` on the div handle is
invoking Puppeteer code to actually simulate user input. It looks
similar to calling `click` on an actual DOM element but is subtly
different.

   ```
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
        headless: false,
        slowMo: 20,
    });
    const page = await browser.newPage();
    await page.setViewport({width: 800, height: 600});
    await page.goto('http://workshop.web1.sunshinectf.org/');

    const start_button = await page.$('button');

    await start_button.click();
    sleep.sleep(1);
    ```

1. Parse the header at the top to determine which div has the puzzle
to answer. Puppeteer has a `$` method similar to jQuery's `$` method
and the more modern `document.querySelector` that allows us to select
the div. Once we have a handle to the div we can get a handle to its
`innerText` property then get its `jsonValue` to transfer the data 
from the browser to our running Node script. The header is always of
the form "with a(n) {id|name|class} of {nnnnn}" so we can use a regex
to pick out these two pieces.

   ```
   const question_h = await page.$('h1#question');
   const innerText_handle = await question_h.getProperty('innerText');
   const innerText = await innerText_handle.jsonValue();

   const matches = innerText.match('Answer the prompt of the gear with a\\(n\\) ([a-z]+) of ([0-9]+)');

   const prop = matches[1];
   const value = matches[2];
   ```

1. Select the specified div and extract the equation. This is similar
to the previous step except we build a selector on the fly based on
what was in the header: `div[prop="value"]`. We once again extract
the contents and this time we just `eval` and convert to an integer:

   ```
   const selector = '[' + prop + '="' + value + '"]';
   const div = await page.$(selector);

   const equation_h3 = await div.$('h3');
   const equation_innerText_handle = await equation_h3.getProperty('innerText');
   const equation = await equation_innerText_handle.jsonValue();

   const answer = Math.floor(eval(equation)).toString();
   ```

1. Supply the answer. Either the form will be a set of radio buttons
or a text box. If it's radio buttons, we find the one whose text is
the same value as the answer and tell Puppeteer to `tap` it.
Otherwise if it's a text box, we tell Puppeteer to `type` the answer
in. The `delay` parameter just tells Puppeteer to wait 5 milliseconds
between each keystroke in order to make it more human-like.

   ```
   const radio = await div.$('input[type=radio][text="' + answer + '"]');

   if (radio) {
       await radio.tap();
   } else {
       const text = await div.$("input[type=text]");
       await text.type(answer, {delay: 5});
   }
   ```

1. Submit by clicking the button, then repeat ad nauseum. Eventually
you are taken to a page with the flag.

   ```
   const button = await div.$('button');
   await button.tap();
   ```
