# Desktop software updates

For desktop apps with GitHub releases, provide **Settings → Software Updates**
with the installed version and a **Check for Updates** button. Also check once
per app launch in the background. Do not open a browser on startup or download
or install an update without user action.

- A startup check must not block onboarding or the dashboard. Only a newer
  release should show a dismissible notice; offline or failed checks stay silent.
  The manual check remains available for an explicit retry.

- Query the project's GitHub `releases/latest` endpoint from the backend with
  a finite timeout. Compare its stable release tag with the running app's
  version using SemVer precedence, ignoring build metadata.
- Show checking, up-to-date, update available, and retryable error states.
  Disable repeated checks while one is in progress. Treat network errors,
  non-success responses, and malformed release versions as check failures.
- When a newer release exists, offer an explicit **View Release** button.
  Open the matching release on the project's GitHub repository.
- Keep the app manifest and package versions aligned with the release tag.
  Test older, equal, newer, prerelease, and invalid versions without using
  the live GitHub API.
