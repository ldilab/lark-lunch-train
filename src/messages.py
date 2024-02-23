import json


def ONBOARD_MESSAGE(user_names: list[str]):
    user_names = [f"@{user}" for user in user_names]
    users = ", ".join(user_names)
    card_obj = {
      "header": {
        "template": "blue",
        "title": {
          "tag": "plain_text",
          "content": "[🚂 LunchTrain] ChooChoo!"
        }
      },
      "elements": [
        {
          "tag": "column_set",
          "flex_mode": "none",
          "background_style": "default",
          "columns": [
            {
              "tag": "column",
              "width": "weighted",
              "weight": 1,
              "vertical_align": "top",
              "elements": [
                {
                  "tag": "div",
                  "text": {
                    "content": "**🔴 장소(Place):**\nXXX",
                    "tag": "lark_md"
                  }
                }
              ]
            },
            {
              "tag": "column",
              "width": "weighted",
              "weight": 1,
              "vertical_align": "top",
              "elements": [
                {
                  "tag": "div",
                  "text": {
                    "content": "**🕐 시간(Time):**\nYY:ZZ",
                    "tag": "lark_md"
                  }
                }
              ]
            }
          ]
        },
        {
          "tag": "column_set",
          "flex_mode": "none",
          "background_style": "default",
          "columns": [
            {
              "tag": "column",
              "width": "weighted",
              "weight": 1,
              "vertical_align": "top",
              "elements": [
                {
                  "tag": "div",
                  "text": {
                    "content": f"**👤 탑승 (On-Board)!**\n{users}",
                    "tag": "lark_md"
                  }
                }
              ]
            }
          ]
        },
        {
          "tag": "hr"
        },
        {
          "tag": "action",
          "actions": [
            {
              "tag": "button",
              "text": {
                "tag": "plain_text",
                "content": "🚂 탑승!"
              },
              "type": "primary",
              "multi_url": {
                "url": "http://ldi.snu.ac.kr:18000/",
                "pc_url": "",
                "android_url": "",
                "ios_url": ""
              },
              "value": {
                "state": "on"
              }
            },
            {
              "tag": "button",
              "text": {
                "tag": "plain_text",
                "content": "👋 하차!"
              },
              "type": "primary",
              "multi_url": {
                "url": "http://ldi.snu.ac.kr:18000/",
                "pc_url": "",
                "android_url": "",
                "ios_url": ""
              },
              "value": {
                "state": "off"
              }
            },
            {
              "tag": "button",
              "text": {
                "tag": "plain_text",
                "content": "❌ 약속 취소"
              },
              "type": "primary",
              "multi_url": {
                "url": "http://ldi.snu.ac.kr:18000/",
                "pc_url": "",
                "android_url": "",
                "ios_url": ""
              },
              "value": {
                "state": "cancel"
              }
            }
          ]
        }
      ]
    }
    return json.dumps(card_obj)
