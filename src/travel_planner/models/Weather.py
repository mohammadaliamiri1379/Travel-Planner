from pydantic import BaseModel, Field


class DayWeather(BaseModel):
	day: int
	date: str = ""
	condition: str = ""
	temp_high_c: float | None = None
	temp_low_c: float | None = None
	precipitation_chance: int | None = None


class WeatherRequest(BaseModel):
	where: str
	when: str = ""
	duration: str = ""


class WeatherResponse(BaseModel):
	forecast: list[DayWeather] = Field(default_factory=list)
