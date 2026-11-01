package com.slowficlock.app;

import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.provider.Settings;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

/**
 * Do Not Disturb for a focus session.
 * Android lets an app change Do Not Disturb only after the person allows it once, in
 * Settings > Do Not Disturb access. After that, the session turns it on and puts back
 * whatever was there before when the session ends.
 */
@CapacitorPlugin(name = "FocusMode")
public class FocusModePlugin extends Plugin {
    private Integer previous = null;

    private NotificationManager nm() {
        return (NotificationManager) getContext().getSystemService(Context.NOTIFICATION_SERVICE);
    }

    @PluginMethod
    public void status(PluginCall call) {
        NotificationManager n = nm();
        JSObject r = new JSObject();
        r.put("available", n != null);
        r.put("granted", n != null && n.isNotificationPolicyAccessGranted());
        r.put("active", n != null && n.getCurrentInterruptionFilter() != NotificationManager.INTERRUPTION_FILTER_ALL);
        call.resolve(r);
    }

    @PluginMethod
    public void openSettings(PluginCall call) {
        Intent i = new Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        getContext().startActivity(i);
        call.resolve();
    }

    @PluginMethod
    public void enable(PluginCall call) {
        NotificationManager n = nm();
        if (n == null || !n.isNotificationPolicyAccessGranted()) {
            call.reject("Do Not Disturb access is not allowed yet", "not_allowed");
            return;
        }
        if (previous == null) previous = n.getCurrentInterruptionFilter();
        n.setInterruptionFilter(NotificationManager.INTERRUPTION_FILTER_PRIORITY);
        call.resolve();
    }

    @PluginMethod
    public void restore(PluginCall call) {
        NotificationManager n = nm();
        if (previous != null && n != null && n.isNotificationPolicyAccessGranted()) {
            n.setInterruptionFilter(previous);
        }
        previous = null;
        call.resolve();
    }
}
