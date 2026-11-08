[app]

# (str) Title of your application
title = Holiday Calendar

# (str) Package name
package.name = holidaycalendar

# (str) Package domain (needed for android package name)
package.domain = org.example

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 0.5

# (list) Application requirements
# Здесь собраны все библиотеки из ваших импортов
requirements = python3, kivy, kivymd, plyer, holidays

# (str) Supported orientations (valid options are: landscape, portrait, all)
orientation = portrait

# =============================================================================
# Android specific
# =============================================================================

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
# Добавлено разрешение на отправку уведомлений (нужно для plyer.notification в Android 13+)
android.permissions = INTERNET, POST_NOTIFICATIONS

# (int) Target Android API
android.api = 34

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use architectural folders
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
