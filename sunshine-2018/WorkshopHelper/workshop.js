// To run:
//
// 1. Make an empty directory with this script and cd to it.
//
// 2. $ npm install puppeteer sleep
//    (this will download a 100-200 MB chrome binary as part of the install)
//
// 3. $ node workshop.js
//    If you get syntax errors about async / await, you need to upgrade to
//    a newer version of nodejs.

const puppeteer = require('puppeteer');
const sleep = require('sleep');

(async () => {
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
        headless: false,
        slowMo: 20,
    });
    const page = await browser.newPage();
    await page.setViewport({width: 000, height: 600});
    await page.goto('http://workshop.web1.sunshinectf.org/');

    // Opening page:
    // Hello there! Welcome to my workshop! ... etc.
    // Need to click [Start] button, only button on page
    const start_button = await page.$('button');
    if (!start_button) {
        throw "no start button";
    }

    await start_button.click();
    sleep.sleep(1);

    while (true) {
        // Now we have this page:
        // <h1 id="question">Answer the prompt of the gear with a(n) (id|name|class) of xxxx</h1>
        const question_h = await page.$('h1#question');
        if (!question_h) {
            throw "no h1 question";
        }

        const innerText_handle = await question_h.getProperty('innerText');
        const innerText = await innerText_handle.jsonValue();

        console.log('div to answer: ' + innerText);

        const matches = innerText.match('Answer the prompt of the gear with a\\(n\\) ([a-z]+) of ([0-9]+)');
        if (!matches) {
            throw "no question_h matches";
        }

        const thing = matches[1];
        const identifier = matches[2];
        const selector = '[' + thing + '="' + identifier + '"]';

        const div = await page.$(selector);
        if (!div) {
            throw "no div with specified selector";
        }

        // OK now we have the div to answer
        // first thing: get the equation in the h3
        const equation_h3 = await div.$('h3');
        const equation_innerText_handle = await equation_h3.getProperty('innerText');
        const equation = await equation_innerText_handle.jsonValue();

        console.log('equation: ', equation);

        const answer = Math.floor(eval(equation)).toString();
        console.log('answer: ', answer);

        // now to input the answer. we have either a radio button to select or an input textbox
        const radio = await div.$('input[type=radio][text="' + answer + '"]');

        if (radio) {
            console.log('radio!');
            await radio.tap();
        } else {
            var text = await div.$("input[type=text]");
            if (text) {
                console.log('text!');
                await text.type(answer, {delay: 5});
            } else {
                throw "don't know how to interact";
            }
        }

        const button = await div.$('button');
        if (!button) {
            throw 'no button';
        }

        await button.tap();
    }

    sleep.sleep(30);

    await browser.close();
    process.exitCode = 0;
})();
