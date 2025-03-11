# App Testing Instructions

- **USE YARN COMMANDS FOR TESTING**: Always use `yarn ios` or `yarn android` when building the app for testing on respective platforms.
- **DO NOT USE EXPO START DIRECTLY**: Prefer using the yarn commands as they ensure proper setup and configuration.
- **CHECK PLATFORM COMPATIBILITY**: Remember that some components may behave differently on iOS vs Android.

```bash
# Build and run on iOS
yarn ios

# Build and run on Android
yarn android

# Run on web platform
yarn web
```
