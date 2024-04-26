# IRIS XML to UDL

An attempt at converting InterSystems IRIS source code in UDL format to
the XML export format. The UDL format is easier to read and is what is
shown and edited in Studio and VS Code. The XML export format, however,
can combine multiple source items in a single export. This can make
deployment considerably easier.

The code here is in early stages, but does already create equivalent (or
even equal, see [below](#equivalent-or-equal)) XML compared to IRIS for
many tested source items. Intended purpose is for use in automated build
processes, possibly involving
[iris-export-builder](https://github.com/gertjanklein/iris-export-builder).
The goal is to make using an IRIS Docker image solely for the conversion
unnecessary.

In addition, the only _safe_ way I know to convert UDL to XML in IRIS is
to use an API (`/api/atelier/v1/namespace/cvt/doc/xml`) that is
deprecated by InterSystems, and appears to be broken in version 2024.1.

Parsing UDL is mainly difficult because it can embed XML, HTML, CSS,
JavaScript, ObjectScript, Python, and more, some of which can internally
switch language again. An additional complication is that the VS Code
ObjectScript plugin appears to allow saving improperly formatted code.

## Equivalent or equal

The IRIS XML export format is very loosely defined. Method keywords, for
example, are placed in elements in the export, but may be present in any
order. If an XML file with such elements is loaded into IRIS, the source
will be exactly the same as if they had been in a different order.

Additionally, the export may escape embedded XML in different ways,
e.g., place everything in a CDATA block, or just escape each XML special
character individually.

An export that may differ from what IRIS would have produced, but
results in exactly the same source in IRIS, is referred to as
_equivalent_.

This is enough for most purposes. However, if comparing a combined
export (created by e.g. iris-export-builder mentioned above) with a
different version, it would be nice if elements appear in the same
order, and escaping is done in the same way. This way, only the actual
differences will show up in the comparison. XML output that is exactly
equal to what IRIS would produce is referred to as _equal_.

An effort has been made to achieve _equal_ exports, but for some XData
blocks, this is currently not possible. In this case, _equivalent_ will
have to do.
