$sourceDir = "D:\Series\Моя прекрасная няня DVDRip"
$seriesTitle = "Моя прекрасная няня"
$seasonNumber = 1
$seriesSlug = "moya-prekrasnaya-nyanya"
$synopsis = "Моя любимая история, к которой я всегда возвращаюсь."
$posterUrl = ""
$mode = "move"

.\windows\import-series.ps1 `
  -SourceDir $sourceDir `
  -SeriesTitle $seriesTitle `
  -SeasonNumber $seasonNumber `
  -SeriesSlug $seriesSlug `
  -Synopsis $synopsis `
  -PosterUrl $posterUrl `
  -Mode $mode
