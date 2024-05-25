import objc
from Foundation import *
from LaunchServices import *
from AppKit import *
from PyObjCTools import AppHelper
from smcdog import manage_speed


status_images = {'idle':'icons/appicon.png', 'idle_h': 'icons/appicon_h.png'}


class Menu(NSObject):
    images = {}
    statusbar = None

    def awakeFromNib(self):
        pass

    def applicationDidFinishLaunching_(self, notification):
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)

        self.images = {
            k: NSImage.alloc().initByReferencingFile_(v) for k, v in status_images.items()
        }

        self.statusitem.setImage_(self.images['idle'])
        self.statusitem.setAlternateImage_(self.images['idle_h'])
        self.statusitem.setHighlightMode_(1)

        self.menu = NSMenu.alloc().init()
        self.info_menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Speed limit is...', '', '')
        self.menu.addItem_(self.info_menuitem)

        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Refresh', 'sync:', '')
        self.menu.addItem_(menuitem)

        menuitem = NSMenuItem.separatorItem()
        self.menu.addItem_(menuitem)
        # Default event
        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(u'Settings...', 'settings:', '')
        self.menu.addItem_(menuitem)

        menuitem = NSMenuItem.separatorItem()
        self.menu.addItem_(menuitem)

        menuitem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(u'Quit', 'terminate:', '')
        self.menu.addItem_(menuitem)
        self.statusitem.setMenu_(self.menu)

        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(NSDate.date(), 5.0, self, 'tick:', None, True)
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        self.timer.fire()

    def applicationWillTerminate_(self, notification):
        """ The hook when the user clicks QUIT in dock """
        pass

    def sync_(self, notification):
        self.update_limit()

    def settings_(self, notification):
        """ Show settings """

    def tick_(self, notification):
        self.update_limit()
    
    @objc.python_method
    def update_limit(self):
        self.info_menuitem.setTitle_(f"Speed limit is {manage_speed()}")


def check_autorun(apppath):
    pool = NSAutoreleasePool.alloc().init()
    try:
        url = CFURLCreateWithFileSystemPath(None, apppath, kCFURLPOSIXPathStyle, True)

        props = NSDictionary.dictionaryWithObject_forKey_(False, kLSSharedFileListItemHidden)

        login_items = LSSharedFileListCreate(
            kCFAllocatorDefault, kLSSharedFileListSessionLoginItems, None)

        NSLog("login_items are %s, url is %s, props are %s" % (login_items, url, props))

        v = LSSharedFileListInsertItemURL(
            login_items,
            kLSSharedFileListItemLast,
            None,
            None,
            url,
            props,
            None
        )
        NSLog("v is %s" % v)

    finally:
        del pool


if __name__ == "__main__":
    nsb = NSBundle.mainBundle()
    check_autorun(nsb.bundlePath())

    app = NSApplication.sharedApplication()
    delegate = Menu.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
