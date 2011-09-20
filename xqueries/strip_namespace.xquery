declare function local:strip-namespace($e as element())
as element()
{
element {local-name($e) }
{
for $child in $e/(@*,node())
return
if ($child instance of element())
then local:strip-namespace($child)
else $child
}
};

for $e in doc("<<<INPUTFILE>>>")/element() return local:strip-namespace($e)
