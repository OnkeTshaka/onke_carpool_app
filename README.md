# OnkeCarpoolApp app

## Run the app

### Set up python environment

On windows

```bash
python -m venv .venv
```

```bash
.venv/scripts/activate
```

On Linux/Mac

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

### Install flet

```bash
pip install "flet[all]"

```

### Run the app

```bash
flet run

```

Might take a while to run on the first try, but everything should run smoothly going forward

## Build the app

### Android

```bash
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```bash
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```bash
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```bash
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```bash
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).

### Web

```bash
flet build web -v
```

For more details on building Web app, refer to the [Web Packaging Guide](https://flet.dev/docs/publish/web/).
