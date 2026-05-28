from config import COMPANY_NAME, BRAND_COLOR, BRAND_LOGO_URL, DEPARTMENTS

DEPT_ICONS = {
    "sales":   "&#128200;",   # 📈
    "account": "&#128196;",   # 📄
    "support": "&#128736;",   # 🔧
    "general": "&#128172;",   # 💬
}


def build_html_email(department: str, reply_body: str) -> str:
    dept_icon  = DEPT_ICONS.get(department, "&#128172;")
    dept_label = department.upper()

    if BRAND_LOGO_URL:
        logo_html = f'''
            <img src="{BRAND_LOGO_URL}" alt="{COMPANY_NAME}"
                 style="width:80px;height:80px;border-radius:50%;
                        object-fit:cover;border:3px solid rgba(255,255,255,0.5);
                        display:block;margin:0 auto 12px;" />
            <span style="font-size:14px;font-weight:600;color:rgba(255,255,255,0.9);
                         letter-spacing:1px;">{COMPANY_NAME}</span>
        '''
    else:
        logo_html = f'<span style="font-size:22px;font-weight:700;letter-spacing:2px;color:white;">{COMPANY_NAME}</span>'

    # Convert plain line breaks to <p> tags
    paragraphs = "".join(
        f"<p style='margin:0 0 14px 0;color:#444444;'>{line}</p>"
        for line in reply_body.strip().split("\n") if line.strip()
    )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

        <!-- HEADER -->
        <tr>
          <td style="background:{BRAND_COLOR};border-radius:14px 14px 0 0;padding:32px 36px 24px;text-align:center;">
            {logo_html}
          </td>
        </tr>

        <!-- DEPARTMENT BANNER — brand blue, white text, no orange -->
        <tr>
          <td style="background:rgba(255,255,255,0.15);
                     background:{BRAND_COLOR};
                     border-top:1px solid rgba(255,255,255,0.2);
                     padding:10px 36px;text-align:center;">
            <span style="color:rgba(255,255,255,0.85);font-size:12px;
                          font-weight:600;letter-spacing:2px;">
              {dept_icon}&nbsp; {dept_label} TEAM
            </span>
          </td>
        </tr>

        <!-- WHITE BODY -->
        <tr>
          <td style="background:#ffffff;padding:36px 40px 28px;
                     font-size:15px;line-height:1.8;">
            {paragraphs}
          </td>
        </tr>

        <!-- DIVIDER -->
        <tr>
          <td style="background:#ffffff;padding:0 40px;">
            <hr style="border:none;border-top:1px solid #eeeeee;margin:0;" />
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="background:#ffffff;border-radius:0 0 14px 14px;
                     padding:18px 40px 28px;text-align:center;">
            <p style="margin:0;font-size:13px;color:#999999;">
              This is an automated reply from
              <strong style="color:{BRAND_COLOR};">{COMPANY_NAME}</strong>.
              Our team will follow up with you shortly.
            </p>
          </td>
        </tr>

        <!-- BOTTOM -->
        <tr>
          <td style="padding:16px;text-align:center;">
            <p style="margin:0;font-size:11px;color:#bbbbbb;">
              &copy; {COMPANY_NAME} &bull; Powered by MailFlow AI
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>

</body>
</html>
""".strip()
