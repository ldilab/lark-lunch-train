import json


def ONBOARD_MESSAGE(
        issuer: str,
        place: str,
        time: str,
        user_names: list[str], is_str: bool = True
):
    user_names = [f"@{user}" for user in user_names]
    users = ", ".join(user_names)
    card_obj = {
        "config": {
            "update_multi": True
        },
        "header": {
            "template": "blue",
            "title": {
                "tag": "plain_text",
                "content": f"[🚂 @{issuer}의 기차] 밥 먹으러 가요!"
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
                                    "content": f"**🔴 장소(Place):**\n{place}",
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
                                    "content": f"**🕐 시간(Time):**\n{time}",
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
                        "type": "danger",
                        "value": {
                            "state": "cancel"
                        }
                    }
                ]
            }
        ]
    }
    if is_str:
        return json.dumps(card_obj)
    return card_obj


def CANCEL_MESSAGE(place, time, is_str):
    card_obj = {
        "config": {
            "update_multi": True
        },
        "header": {
            "template": "red",
            "title": {
                "tag": "plain_text",
                "content": "[🚂 LunchTrain] Engine Stop! 약속 취소!"
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
                                    "content": f"**🔴 장소(Place):**\n{place}",
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
                                    "content": f"**🕐 시간(Time):**\n{time}",
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
                        "elements": []
                    }
                ]
            }
        ]
    }
    if is_str:
        return json.dumps(card_obj)
    return card_obj
