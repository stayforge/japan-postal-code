"""
Pydantic models for Japan Postal Code data.
Based on Japan Post CSV format specification.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal


class JapanPostalCode(BaseModel):
    """
    Japan Postal Code data model.
    Based on Japan Post CSV format specification.
    """
    
    # 全国地方公共団体コード（JIS X0401、X0402）
    local_government_code: str = Field(
        None,
        summary="Local Government Code",
        description="Local government code (JIS X0401, X0402)\nHalf-width numeric characters"
    )
    
    # （旧）郵便番号（5桁）
    old_postal_code: str = Field(
        None,
        summary="Old Postal Code",
        description="Old postal code (5 digits)\nHalf-width numeric characters"
    )
    
    # 郵便番号（7桁）
    postal_code: str = Field(
        None,
        summary="Postal Code",
        description="Postal code (7 digits)\nHalf-width numeric characters"
    )
    
    # 都道府県名（カタカナ）
    prefecture_name_kana: str = Field(
        None,
        summary="Prefecture Name (Katakana)",
        description="Prefecture name in Katakana\nFull-width Katakana characters\nListed in code order (Note 1)"
    )
    
    # 市区町村名（カタカナ）
    city_name_kana: str = Field(
        None,
        summary="City/Ward/Town/Village Name (Katakana)",
        description="City/Ward/Town/Village name in Katakana\nFull-width Katakana characters\nListed in code order (Note 1)"
    )
    
    # 町域名（カタカナ）
    town_name_kana: str = Field(
        None,
        summary="Town Name (Katakana)",
        description="Town name in Katakana\nFull-width Katakana characters\nListed in Gojuon order (Note 1)"
    )
    
    # 都道府県名（漢字）
    prefecture_name: str = Field(
        None,
        summary="Prefecture Name (Kanji)",
        description="Prefecture name in Kanji\nListed in code order (Note 1, 2)"
    )
    
    # 市区町村名（漢字）
    city_name: str = Field(
        None,
        summary="City/Ward/Town/Village Name (Kanji)",
        description="City/Ward/Town/Village name in Kanji\nListed in code order (Note 1, 2)"
    )
    
    # 町域名（漢字）
    town_name: str = Field(
        None,
        summary="Town Name (Kanji)",
        description="Town name in Kanji\nListed in Gojuon order (Note 1, 2)"
    )
    
    # 一町域が二以上の郵便番号で表される場合の表示
    multiple_postal_codes_per_town: Literal["0", "1"] = Field(
        None,
        summary="Multiple Postal Codes per Town",
        description="Flag indicating if one town area is represented by two or more postal codes (Note 3)\n'1' = applicable, '0' = not applicable"
    )
    
    # 小字毎に番地が起番されている町域の表示
    koaza_numbering: Literal["0", "1"] = Field(
        None,
        summary="Koaza Numbering",
        description="Flag indicating if addresses are numbered for each Koaza (small area) (Note 4)\n'1' = applicable, '0' = not applicable"
    )
    
    # 丁目を有する町域の場合の表示
    has_chome: Literal["0", "1"] = Field(
        None,
        summary="Has Chome",
        description="Flag indicating if the town area has Chome (numbered blocks)\n'1' = applicable, '0' = not applicable"
    )
    
    # 一つの郵便番号で二以上の町域を表す場合の表示
    multiple_towns_per_postal_code: Literal["0", "1"] = Field(
        None,
        summary="Multiple Towns per Postal Code",
        description="Flag indicating if one postal code represents two or more town areas (Note 5)\n'1' = applicable, '0' = not applicable"
    )
    
    # 更新の表示
    update_status: Literal["0", "1", "2"] = Field(
        None,
        summary="Update Status",
        description="Update status (Note 6)\n'0' = no change\n'1' = changed\n'2' = abolished (used only in abolished data)"
    )
    
    # 変更理由
    change_reason: Literal["0", "1", "2", "3", "4", "5", "6"] = Field(
        None,
        summary="Change Reason",
        description="Reason for change\n'0' = no change\n'1' = municipal reorganization (city/ward/town/village/district reorganization, ordinance-designated city enforcement)\n'2' = implementation of address indication\n'3' = land readjustment\n'4' = postal area adjustment, etc.\n'5' = correction\n'6' = abolished (used only in abolished data)"
    )
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        """Validate postal code is 7 digits."""
        if v is None:
            raise ValueError('Postal code cannot be None')
        # Strip whitespace first
        v = v.strip()
        if len(v) != 7 or not v.isdigit():
            raise ValueError(f'Postal code must be 7 digits, got: {repr(v)}')
        return v
    
    @field_validator('old_postal_code')
    @classmethod
    def validate_old_postal_code(cls, v: str) -> str:
        """Validate old postal code is 3 or 5 digits."""
        if v is None:
            return None
        # Strip whitespace first
        v = v.strip()
        # Allow empty string (will be None)
        if not v:
            return None
        # Validate length and digits
        if not (len(v) in [3, 5]) or not v.isdigit():
            raise ValueError(f'Old postal code must be 3 or 5 digits, got: {repr(v)}')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "local_government_code": "01101",
                "old_postal_code": "06000",
                "postal_code": "0600000",
                "prefecture_name_kana": "ホッカイドウ",
                "city_name_kana": "サッポロシチュウオウク",
                "town_name_kana": "イカニケイサイガナイバアイ",
                "prefecture_name": "北海道",
                "city_name": "札幌市中央区",
                "town_name": "以下に掲載がない場合",
                "multiple_postal_codes_per_town": "0",
                "koaza_numbering": "0",
                "has_chome": "0",
                "multiple_towns_per_postal_code": "0",
                "update_status": "0",
                "change_reason": "0"
            }
        }
    )

