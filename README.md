# Steam price notifier
Notifies you of price changes (and discounts) to Steam store products in your wishlist and follow list

[Article for this project](https://asbra.net/steam-price-tracker/) (link to my blog)

## Installation
* Edit [steam-discount-check.py](steam-discount-check.py) set up `config` variables
* Give write permission, script writes to `_log.txt` and `wishlist.json` in script folder

### Configuration
* `region` price region, set to country code of the country on your Steam store account
* `steamid` your Steam vanity name/nick name "novoc" in https://steamcommunity.com/id/novoc/
* `currency` currency symbol (just aesthetic)
* `mail_from` FROM address in email alert
* `mail_to` TO address in email alert (leave blank to disable email alerts)
