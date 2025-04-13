from dash import html


def get_reference_tables():
    """
    Returns the HTML structure for the Allen interval composition reference tables.
    """
    return html.Div(
        [
            # Table A: Display as regular table with heading
            html.H5("Basic Interval Composition", className="mt-1 mb-1"),
            html.Div(
                html.Table(
                    [
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("", style={"width": "60px"}),
                                    # All columns have the same fixed width
                                    *[
                                        html.Th(
                                            html.Div(content),
                                            style={"width": "60px"},
                                        )
                                        for content in [
                                            [
                                                html.Strong("p"),
                                                html.Span("\u00a0"),
                                                html.Sub("before"),
                                            ],
                                            [
                                                html.Strong("m"),
                                                html.Span("\u00a0"),
                                                html.Sub("meets"),
                                            ],
                                            [
                                                html.Strong("o"),
                                                html.Span("\u00a0"),
                                                html.Sub("overlaps"),
                                            ],
                                            [
                                                html.Strong("F"),
                                                html.Span("\u00a0"),
                                                html.Sub("finished\u00a0by"),
                                            ],
                                            [
                                                html.Strong("D"),
                                                html.Span("\u00a0"),
                                                html.Sub("contains"),
                                            ],
                                            [
                                                html.Strong("s"),
                                                html.Span("\u00a0"),
                                                html.Sub("starts"),
                                            ],
                                            [
                                                html.Strong("e"),
                                                html.Span("\u00a0"),
                                                html.Sub("equals"),
                                            ],
                                            [
                                                html.Strong("S"),
                                                html.Span("\u00a0"),
                                                html.Sub("started\u00a0by"),
                                            ],
                                            [
                                                html.Strong("d"),
                                                html.Span("\u00a0"),
                                                html.Sub("during"),
                                            ],
                                            [
                                                html.Strong("f"),
                                                html.Span("\u00a0"),
                                                html.Sub("finishes"),
                                            ],
                                            [
                                                html.Strong("O"),
                                                html.Span("\u00a0"),
                                                html.Sub("overlapped\u00a0by"),
                                            ],
                                            [
                                                html.Strong("M"),
                                                html.Span("\u00a0"),
                                                html.Sub("met\u00a0by"),
                                            ],
                                            [
                                                html.Strong("P"),
                                                html.Span("\u00a0"),
                                                html.Sub("after"),
                                            ],
                                        ]
                                    ],
                                ]
                            )
                        ),
                        html.Tbody(
                            [
                                # p (before)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("p"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("before"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(pmosd)", className="pmosd"),
                                        html.Td("(pmosd)", className="pmosd"),
                                        html.Td("(pmosd)", className="pmosd"),
                                        html.Td("(pmosd)", className="pmosd"),
                                        html.Td(html.I("full"), className="full"),
                                    ]
                                ),
                                # m (meets)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("m"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("meets"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(m)", className="m"),
                                        html.Td("(m)", className="m"),
                                        html.Td("(m)", className="m"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td("(Fef)", className="Fef"),
                                        html.Td("(DSOMP)", className="DSOMP"),
                                    ]
                                ),
                                # o (overlaps)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("o"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("overlaps"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(pmo)", className="pmo"),
                                        html.Td("(pmo)", className="pmo"),
                                        html.Td("(pmoFD)", className="pmoFD"),
                                        html.Td("(o)", className="o"),
                                        html.Td("(o)", className="o"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td(html.I("concur"), className="concur"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(DSOMP)", className="DSOMP"),
                                    ]
                                ),
                                # F (finished by)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("F"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("finished\u00a0by"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(m)", className="m"),
                                        html.Td("(o)", className="o"),
                                        html.Td("(F)", className="F"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(o)", className="o"),
                                        html.Td("(F)", className="F"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td("(Fef)", className="Fef"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(DSOMP)", className="DSOMP"),
                                    ]
                                ),
                                # D (contains)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("D"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("contains"),
                                                ]
                                            )
                                        ),
                                        html.Td("(pmoFD)", className="pmoFD"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(D)", className="D"),
                                        html.Td(html.I("concur"), className="concur"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(DSOMP)", className="DSOMP"),
                                    ]
                                ),
                                # s (starts)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("s"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("starts"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(pmo)", className="pmo"),
                                        html.Td("(pmo)", className="pmo"),
                                        html.Td("(pmoFD)", className="pmoFD"),
                                        html.Td("(s)", className="s"),
                                        html.Td("(s)", className="s"),
                                        html.Td("(seS)", className="seS"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td("(M)", className="M"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                                # e (equals)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("e"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("equals"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(m)", className="m"),
                                        html.Td("(o)", className="o"),
                                        html.Td("(F)", className="F"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(s)", className="s"),
                                        html.Td("(e)", className="e"),
                                        html.Td("(S)", className="S"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(f)", className="f"),
                                        html.Td("(O)", className="O"),
                                        html.Td("(M)", className="M"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                                # S (started by)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("S"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("started\u00a0by"),
                                                ]
                                            )
                                        ),
                                        html.Td("(pmoFD)", className="pmoFD"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(D)", className="D"),
                                        html.Td("(seS)", className="seS"),
                                        html.Td("(S)", className="S"),
                                        html.Td("(S)", className="S"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td("(O)", className="O"),
                                        html.Td("(O)", className="O"),
                                        html.Td("(M)", className="M"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                                # d (during)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("d"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("during"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(pmosd)", className="pmosd"),
                                        html.Td("(pmosd)", className="pmosd"),
                                        html.Td(html.I("full"), className="full"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(dfOMP)", className="dfOMP"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(dfOMP)", className="dfOMP"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                                # f (finishes)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("f"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("finishes"),
                                                ]
                                            )
                                        ),
                                        html.Td("(p)", className="p"),
                                        html.Td("(m)", className="m"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td("(Fef)", className="Fef"),
                                        html.Td("(DSOMP)", className="DSOMP"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(f)", className="f"),
                                        html.Td("(OMP)", className="OMP"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(f)", className="f"),
                                        html.Td("(OMP)", className="OMP"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                                # O (overlapped by)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("O"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("overlapped\u00a0by"),
                                                ]
                                            )
                                        ),
                                        html.Td("(pmoFD)", className="pmoFD"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td(html.I("concur"), className="concur"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(DSOMP)", className="DSOMP"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td("(O)", className="O"),
                                        html.Td("(OMP)", className="OMP"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td("(O)", className="O"),
                                        html.Td("(OMP)", className="OMP"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                                # M (met by)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("M"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("met\u00a0by"),
                                                ]
                                            )
                                        ),
                                        html.Td("(pmoFD)", className="pmoFD"),
                                        html.Td("(seS)", className="seS"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td("(M)", className="M"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td("(M)", className="M"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td("(M)", className="M"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                                # P (after)
                                html.Tr(
                                    [
                                        html.Th(
                                            html.Div(
                                                [
                                                    html.Strong("P"),
                                                    html.Span("\u00a0"),
                                                    html.Sub("after"),
                                                ]
                                            )
                                        ),
                                        html.Td(html.I("full"), className="full"),
                                        html.Td("(dfOMP)", className="dfOMP"),
                                        html.Td("(dfOMP)", className="dfOMP"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(dfOMP)", className="dfOMP"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(dfOMP)", className="dfOMP"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                        html.Td("(P)", className="P"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    className="table table-sm table-bordered composition",
                    style={
                        "fontSize": "0.75rem",
                        "width": "100%",
                        "tableLayout": "fixed",
                    },
                ),
                className="overflow-auto mb-1",
            ),
            # Table B: Display as regular table with heading
            html.H5("Composition Frequencies", className="mt-1 mb-1"),
            html.Div(
                html.Table(
                    [
                        html.Tbody(
                            [
                                html.Tr(
                                    [
                                        html.Th("22"),
                                        html.Td("(p)", className="p"),
                                        html.Td("(P)", className="P"),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Th("9"),
                                        html.Td("(d)", className="d"),
                                        html.Td("(D)", className="D"),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Th("7"),
                                        html.Td("(oFD)", className="oFD"),
                                        html.Td("(osd)", className="osd"),
                                        html.Td("(DSO)", className="DSO"),
                                        html.Td("(dfO)", className="dfO"),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Th("6"),
                                        html.Td("(pmoFD)", className="pmoFD"),
                                        html.Td("(pmosd)", className="pmosd"),
                                        html.Td("(m)", className="m"),
                                        html.Td("(DSOMP)", className="DSOMP"),
                                        html.Td("(dfOMP)", className="dfOMP"),
                                        html.Td("(M)", className="M"),
                                        html.Td(""),
                                        html.Td(""),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Th("5"),
                                        html.Td("(o)", className="o"),
                                        html.Td("(O)", className="O"),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Th("4"),
                                        html.Td("(pmo)", className="pmo"),
                                        html.Td("(OMP)", className="OMP"),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Th("3"),
                                        html.Td(html.I("full"), className="full"),
                                        html.Td(html.I("concur"), className="concur"),
                                        html.Td("(F)", className="F"),
                                        html.Td("(Fef)", className="Fef"),
                                        html.Td("(seS)", className="seS"),
                                        html.Td("(s)", className="s"),
                                        html.Td("(S)", className="S"),
                                        html.Td("(f)", className="f"),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Th("1"),
                                        html.Td("(e)", className="e"),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                        html.Td(""),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    className="table table-sm table-bordered composition",
                    style={
                        "fontSize": "0.8rem",
                        "tableLayout": "fixed",
                        "width": "100%",
                    },
                ),
                className="overflow-auto mb-1",
            ),
        ],
        className="composition-reference",
    )
