# Notchwork

A six-rotor cipher machine with a notch key. Type a message and the screen shows the coded text. Type the coded text into a machine set to the same key, and the original message comes back.

It runs in any browser, installs as an app on Android and Windows, and works offline. A Python version of the same machine sits beside it, and the two give identical output.

Try it once you have published it (see below): `https://YOUR-USERNAME.github.io/notchwork/`

## The key

Sender and receiver must enter the same two settings, or the message will not decode.

- **Notches** are six symbols, one per rotor, such as `L-I-G-W-M-C`. A rotor pushes its left-hand neighbour one step forward when it sits on its notch. Agree on these in advance and change them regularly.
- **Start position** is six symbols, such as `S-S-S-S-S-S`, one per rotor. This is where each rotor begins. Set it fresh for every message.

Symbols are the letters A to Z and the digits 0 to 9. Spaces and basic punctuation pass through uncoded. Lowercase input becomes uppercase.

## Using the web app

Open `index.html` in a browser, or visit your published copy.

- Press **Notch** to open the rotor lids. Click a rotor, then type a symbol or drag its wheel. Press **Notch** again to close the lids.
- Set the start position by dragging the wheels, scrolling over them, or clicking a rotor and pressing the up and down arrow keys. Push the red slider to **S** to save it.
- Type on your keyboard or tap the on-screen keys. The pressed key lights up and the screen shows the coded text.
- Push the slider to **R** to rewind the rotors to the saved start. Backspace undoes the last symbol. **Clear** wipes the screen.

Notches and the saved start position stay in your browser between visits. They never leave your device.

Sounds are on by default: a typewriter click for every key, a tick each time you turn a rotor by hand, a slide and clunk from the red slider, and a heavy thud when the lids open and close. They are generated in the browser, so nothing downloads and they work offline. Press **Sound on** under the screen to mute them.

## Using the Python version

Python 3 is the only requirement.

```
python notchwork.py "MEET AT 21:30" --notches L-I-G-W-M-C --start S-S-S-S-S-S
python notchwork.py "2JP2 05 AR:XO" --notches L-I-G-W-M-C --start S-S-S-S-S-S
python notchwork.py --interactive
```

The first command prints `2JP2 05 AR:XO`. The second reverses it. Add `--strip` to drop spaces and punctuation from the output.

## Install it as an app

Install works once the site is published at an `https` address.

- **Android:** open the site in Chrome, open the menu, and choose **Install app** (or **Add to Home screen**).
- **Windows:** open the site in Edge or Chrome and click the install icon at the right end of the address bar.

## Publish your own copy

1. Create a free account at github.com and make a new public repository named `notchwork`.
2. On the repository page, choose **Add file**, then **Upload files**. Drag in everything from this folder, including the hidden `.github` folder, and commit.
3. Open **Settings**, then **Pages**. Under **Build and deployment**, set the source to **Deploy from a branch**, pick the `main` branch and the `/ (root)` folder, and save.
4. After a minute or two, the page shows your site address.

The **Actions** tab runs the tests on every change.

## Tests

```
python -m unittest discover -s tests -v
node tests/check_web.js
```

Both read `tests/vectors.json`, so a change that makes the web app and the Python version disagree fails the build.

## How it works

Each rotor is a fixed scramble of the 36 symbols. A key press sends the signal through all six rotors, off a reflector that pairs the symbols, and back through the rotors in reverse. Before each press, the right-hand rotor steps forward, and any rotor sitting on its notch carries the one to its left forward with it.

Because the reflector pairs symbols, the machine is its own inverse. It also means a symbol never codes to itself.

This is not a copy of the historical Enigma. The 36-symbol alphabet, all the rotor wirings, and the reflector are original, the notches are part of the key instead of being fixed in the rotors, and there is no plugboard.

## Security

Notchwork is a toy and a learning project. Machines of this design have structural weaknesses that attackers can exploit without guessing the key. Do not use it to protect anything private. For real secrecy, use a modern tool built on AES.

## Inspiration

The look and the controls take inspiration from the OBSCURA machine in the game False Echo. This project has no affiliation with the game or its makers.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole web app in one file |
| `notchwork.py` | The Python command-line version |
| `manifest.webmanifest`, `sw.js`, `icons/` | Make the site installable and usable offline |
| `tests/` | Python tests, a Node check for the web app, and shared vectors |
| `.github/workflows/tests.yml` | Runs the tests on GitHub |
