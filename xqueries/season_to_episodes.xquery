(: episode list :)
(: input: a single season page :)
let $season := doc("<<<INPUTFILE>>>")//div[@class="post-content"]
let $endl := "&#10;"

let $info := (
	<info original="Dauer" translation="duration" />
	,<info original="Größe" translation="size" />
	,<info original="Format" translation="format" />
	,<info original="Sprache" translation="language" />
)
let $entries := $season/p/strong/text()[contains(., "Dauer") or contains(., "Download")]/../..
return
	for $entry in $entries
		let $linktext := $entry/text()[contains(., "rapidshare.com")]
		let $probable_title := normalize-space(string-join($entry/strong[1]/text(), ""))
		return
		(
			if (contains($entry/strong[2]/text(), "Download"))
			then
				(
					"BEGIN EPISODE"
					, $endl
					, concat(
						"title "
						, $probable_title
					)
					, $endl
					, concat(
						"link "
						,$linktext[1]/preceding-sibling::a[1]/@href/data(.)
						,if (count($linktext) > 1)	then concat($endl, "error more than one link found") else ""
					)
					, $endl
					, "END EPISODE"
					, $endl
				)
			else
				(
				"BEGIN HEADER"
				, $endl
				, for $piece in $info
						return concat(
							$piece/@translation, " ",
							normalize-space(
								substring-before(
									$entry/strong[
										contains(
											string-join(text(), ""),
											$piece/@original)
									][1]/following-sibling::text()[1]
									, "|")
							),
							$endl
							)
				, "END HEADER"
				, $endl
				)
		)
