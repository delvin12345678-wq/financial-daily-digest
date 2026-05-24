/* Meta Pixel base + helpers
 * 用法:在 HTML 設 <script>window.META_PIXEL_ID="123456789"</script> 再 include 此檔
 * 沒設 PIXEL_ID 時整支 noop,production 安全。
 * 之後在轉換點呼 mdTrackLead() / mdTrackPurchase({email, value, currency}) 即可。
 */
(function () {
  if (!window.META_PIXEL_ID) return; // 沒設就不載入,避免 console error

  // 標準 Meta Pixel base code
  !(function (f, b, e, v, n, t, s) {
    if (f.fbq) return;
    n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
    if (!f._fbq) f._fbq = n;
    n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = [];
    t = b.createElement(e); t.async = !0; t.src = v;
    s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
  })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");

  fbq("init", window.META_PIXEL_ID);
  fbq("track", "PageView");
})();

// 訂閱成功 → Lead event(配合 server-side Conversions API 雙寫,Meta 自動 dedupe)
window.mdTrackLead = function (opts) {
  if (!window.fbq) return;
  const eventId = (opts && opts.eventId) || (Date.now().toString(36) + Math.random().toString(36).slice(2, 10));
  try {
    fbq("track", "Lead", {
      content_name: (opts && opts.plan) || "free",
      content_category: "subscription",
    }, { eventID: eventId });
  } catch (e) { /* silent */ }
  return eventId;
};

// Premium 試讀付款成功 → Purchase event(client-side 補強,server-side 才是真的權威來源)
window.mdTrackPurchase = function (opts) {
  if (!window.fbq) return;
  const eventId = (opts && opts.eventId) || (Date.now().toString(36) + Math.random().toString(36).slice(2, 10));
  try {
    fbq("track", "Purchase", {
      value: (opts && opts.value) || 299,
      currency: (opts && opts.currency) || "TWD",
      content_name: "premium_trial",
    }, { eventID: eventId });
  } catch (e) { /* silent */ }
  return eventId;
};
