# ytmusic-feed

*Tool to create a ~~curated~~ feed of new releases from the artists you follow in chronological order. Why this isn't a 1st-party feature might just radicalize me.*

## Requirements

- [Python 3.13](https://www.python.org/downloads/) (add to system path when prompted)

## How To Use

1. Sign into the [Google Cloud Console](https://console.cloud.google.com/projectselector2/apis/credentials) with the Google account associated with your YouTube Music library.

2. Create a new project.

3. Create an **OAuth Client ID** for your newly created project (you may have to configure some "branding" information for your project before you may begin this step) Select **TVs and Limited Input devices** when prompted for the application type.

4. Select "Download JSON" and keep the file somewhere secure (you only get to download this file once).

5. Visit the [Audience](https://console.cloud.google.com/auth/audience) tab in Google Cloud. Add the email address of Google Account which your YouTube Music library is associated with

6. Run

7. Visit the provided URL and enter the code displayed on screen. You may see a warning "Google hasn’t verified this app", but can press **Continue** to proeed anyways.

8. 