import type { CredibilityScorecard } from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Registry
// Scores are heuristic reliability priors (0-100). Threshold = 70.
// ─────────────────────────────────────────────────────────────────────────────

export const CREDIBILITY_THRESHOLD = 70;

export const CREDIBLE_SOURCES: Record<string, { score: number; label: string }> = {
  "apnews.com":                    { score: 98, label: "International Wire Service" },
  "cdc.gov":                       { score: 98, label: "Government Health Authority" },
  "nasa.gov":                      { score: 98, label: "Space Agency" },
  "nih.gov":                       { score: 98, label: "Government Health Research" },
  "reuters.com":                   { score: 98, label: "International Wire Service" },
  "un.org":                        { score: 98, label: "International Organization" },
  "who.int":                       { score: 98, label: "International Health Authority" },
  "bls.gov":                       { score: 97, label: "Government Statistics" },
  "census.gov":                    { score: 97, label: "Government Statistics" },
  "fda.gov":                       { score: 97, label: "Government Regulator" },
  "noaa.gov":                      { score: 97, label: "Government Science Agency" },
  "sec.gov":                       { score: 97, label: "Financial Regulator" },
  "usgs.gov":                      { score: 97, label: "Government Science Agency" },
  "abs.gov.au":                    { score: 96, label: "Government Statistics" },
  "archives.gov":                  { score: 96, label: "National Archives" },
  "bankofengland.co.uk":           { score: 96, label: "Central Bank" },
  "bea.gov":                       { score: 96, label: "Government Statistics" },
  "congress.gov":                  { score: 96, label: "Government Legislative Source" },
  "data.gov":                      { score: 96, label: "Government Data Portal" },
  "ecb.europa.eu":                 { score: 96, label: "Central Bank" },
  "epa.gov":                       { score: 96, label: "Government Science Agency" },
  "esa.int":                       { score: 96, label: "Space Agency" },
  "faa.gov":                       { score: 96, label: "Government Regulator" },
  "ftc.gov":                       { score: 96, label: "Government Regulator" },
  "gao.gov":                       { score: 96, label: "Government Audit Agency" },
  "imf.org":                       { score: 96, label: "International Financial Institution" },
  "isro.gov.in":                   { score: 96, label: "Space Agency" },
  "jpl.nasa.gov":                  { score: 96, label: "Space Agency" },
  "loc.gov":                       { score: 96, label: "National Library" },
  "ncbi.nlm.nih.gov":              { score: 96, label: "Biomedical Research Repository" },
  "nejm.org":                      { score: 96, label: "Medical Journal" },
  "ons.gov.uk":                    { score: 96, label: "Government Statistics" },
  "pubmed.ncbi.nlm.nih.gov":       { score: 96, label: "Medical Literature Index" },
  "rbi.org.in":                    { score: 96, label: "Central Bank" },
  "singstat.gov.sg":               { score: 96, label: "Government Statistics" },
  "stat.go.jp":                    { score: 96, label: "Government Statistics" },
  "statcan.gc.ca":                 { score: 96, label: "Government Statistics" },
  "stats.govt.nz":                 { score: 96, label: "Government Statistics" },
  "supremecourt.gov":              { score: 96, label: "Judicial Authority" },
  "unicef.org":                    { score: 96, label: "International Organization" },
  "usa.gov":                       { score: 96, label: "Government Source" },
  "uscourts.gov":                  { score: 96, label: "Judicial Authority" },
  "worldbank.org":                 { score: 96, label: "International Financial Institution" },
  "afp.com":                       { score: 95, label: "International Wire Service" },
  "bankofcanada.ca":               { score: 95, label: "Central Bank" },
  "bis.org":                       { score: 95, label: "International Financial Institution" },
  "boj.or.jp":                     { score: 95, label: "Central Bank" },
  "ec.europa.eu":                  { score: 95, label: "Institutional Source" },
  "eci.gov.in":                    { score: 95, label: "Election Authority" },
  "europa.eu":                     { score: 95, label: "Institutional Source" },
  "iaea.org":                      { score: 95, label: "International Organization" },
  "icrc.org":                      { score: 95, label: "Humanitarian Organization" },
  "imd.gov.in":                    { score: 95, label: "Meteorological Agency" },
  "india.gov.in":                  { score: 95, label: "Government Source" },
  "indiacode.nic.in":              { score: 95, label: "Government Legal Source" },
  "pib.gov.in":                    { score: 95, label: "Government Source" },
  "rba.gov.au":                    { score: 95, label: "Central Bank" },
  "sebi.gov.in":                   { score: 95, label: "Financial Regulator" },
  "supremecourtofindia.nic.in":    { score: 95, label: "Judicial Authority" },
  "unesco.org":                    { score: 95, label: "International Organization" },
  "australia.gov.au":              { score: 94, label: "Government Source" },
  "barc.gov.in":                   { score: 94, label: "Research Agency" },
  "cag.gov.in":                    { score: 94, label: "Government Audit Agency" },
  "caltech.edu":                   { score: 94, label: "Academic Institution" },
  "cam.ac.uk":                     { score: 94, label: "Academic Institution" },
  "canada.ca":                     { score: 94, label: "Government Source" },
  "cell.com":                      { score: 94, label: "Scientific Publisher" },
  "cfr.gov":                       { score: 94, label: "Government Legal Source" },
  "coe.int":                       { score: 94, label: "International Organization" },
  "data.europa.eu":                { score: 94, label: "Government Data Portal" },
  "drdo.gov.in":                   { score: 94, label: "Defence Research Agency" },
  "egazette.nic.in":               { score: 94, label: "Government Legal Source" },
  "energy.gov":                    { score: 94, label: "Government Science Agency" },
  "ethz.ch":                       { score: 94, label: "Academic Institution" },
  "fao.org":                       { score: 94, label: "International Organization" },
  "fbi.gov":                       { score: 94, label: "Law Enforcement Agency" },
  "gov.au":                        { score: 94, label: "Government Source" },
  "gov.in":                        { score: 94, label: "Government Source" },
  "gov.jp":                        { score: 94, label: "Government Source" },
  "gov.sg":                        { score: 94, label: "Government Source" },
  "gov.uk":                        { score: 94, label: "Government Source" },
  "govt.nz":                       { score: 94, label: "Government Source" },
  "harvard.edu":                   { score: 94, label: "Academic Institution" },
  "icao.int":                      { score: 94, label: "International Organization" },
  "icj-cij.org":                   { score: 94, label: "International Court" },
  "icmr.gov.in":                   { score: 94, label: "Medical Research Organization" },
  "ilo.org":                       { score: 94, label: "International Organization" },
  "imo.org":                       { score: 94, label: "International Organization" },
  "interpol.int":                  { score: 94, label: "International Organization" },
  "itu.int":                       { score: 94, label: "International Organization" },
  "jamanetwork.com":               { score: 94, label: "Medical Journal" },
  "justice.gov":                   { score: 94, label: "Government Legal Source" },
  "legislative.gov.in":            { score: 94, label: "Government Legal Source" },
  "mea.gov.in":                    { score: 94, label: "Government Ministry" },
  "mha.gov.in":                    { score: 94, label: "Government Ministry" },
  "mit.edu":                       { score: 94, label: "Academic Institution" },
  "mohfw.gov.in":                  { score: 94, label: "Government Ministry" },
  "nature.com":                    { score: 94, label: "Scientific Publisher" },
  "nhs.uk":                        { score: 94, label: "Public Health Service" },
  "nps.gov":                       { score: 94, label: "Government Agency" },
  "oecd.org":                      { score: 94, label: "International Organization" },
  "ohchr.org":                     { score: 94, label: "International Organization" },
  "ox.ac.uk":                      { score: 94, label: "Academic Institution" },
  "parliament.uk":                 { score: 94, label: "Legislative Source" },
  "pnas.org":                      { score: 94, label: "Scientific Journal" },
  "princeton.edu":                 { score: 94, label: "Academic Institution" },
  "regulations.gov":               { score: 94, label: "Government Regulatory Source" },
  "royalsociety.org":              { score: 94, label: "Scientific Society" },
  "royalsocietypublishing.org":    { score: 94, label: "Scientific Publisher" },
  "science.org":                   { score: 94, label: "Scientific Publisher" },
  "sciencemag.org":                { score: 94, label: "Scientific Publisher" },
  "si.edu":                        { score: 94, label: "Research Institution" },
  "stanford.edu":                  { score: 94, label: "Academic Institution" },
  "state.gov":                     { score: 94, label: "Government Ministry" },
  "thelancet.com":                 { score: 94, label: "Medical Journal" },
  "undp.org":                      { score: 94, label: "International Organization" },
  "unep.org":                      { score: 94, label: "International Organization" },
  "unhcr.org":                     { score: 94, label: "International Organization" },
  "usda.gov":                      { score: 94, label: "Government Agency" },
  "wmo.int":                       { score: 94, label: "International Organization" },
  "wto.org":                       { score: 94, label: "International Organization" },
  "yale.edu":                      { score: 94, label: "Academic Institution" },
  "acm.org":                       { score: 92, label: "Professional Organization" },
  "agu.org":                       { score: 92, label: "Scientific Society" },
  "ams.org":                       { score: 92, label: "Scientific Society" },
  "aps.org":                       { score: 92, label: "Scientific Society" },
  "berkeley.edu":                  { score: 92, label: "Academic Institution" },
  "bloomberg.com":                 { score: 92, label: "Financial News" },
  "bmj.com":                       { score: 92, label: "Medical Journal" },
  "cbic.gov.in":                   { score: 92, label: "Government Tax Authority" },
  "cochranelibrary.com":           { score: 92, label: "Medical Evidence" },
  "columbia.edu":                  { score: 92, label: "Academic Institution" },
  "cornell.edu":                   { score: 92, label: "Academic Institution" },
  "csir.res.in":                   { score: 92, label: "Research Organization" },
  "defense.gov":                   { score: 92, label: "Government Ministry" },
  "dst.gov.in":                    { score: 92, label: "Government Science Ministry" },
  "duke.edu":                      { score: 92, label: "Academic Institution" },
  "economist.com":                 { score: 92, label: "Premium News Magazine" },
  "epfl.ch":                       { score: 92, label: "Academic Institution" },
  "europarl.europa.eu":            { score: 92, label: "Institutional Source" },
  "factcheck.org":                 { score: 92, label: "Fact-Checker" },
  "ft.com":                        { score: 92, label: "Financial News" },
  "gov.ca":                        { score: 92, label: "Government Source" },
  "gst.gov.in":                    { score: 92, label: "Government Tax Authority" },
  "icar.gov.in":                   { score: 92, label: "Research Organization" },
  "icc-cpi.int":                   { score: 92, label: "International Court" },
  "iisc.ac.in":                    { score: 92, label: "Academic Institution" },
  "imperial.ac.uk":                { score: 92, label: "Academic Institution" },
  "incometax.gov.in":              { score: 92, label: "Government Tax Authority" },
  "kyoto-u.ac.jp":                 { score: 92, label: "Academic Institution" },
  "loksabha.nic.in":               { score: 92, label: "Legislative Source" },
  "lse.ac.uk":                     { score: 92, label: "Academic Institution" },
  "mca.gov.in":                    { score: 92, label: "Government Ministry" },
  "mib.gov.in":                    { score: 92, label: "Government Ministry" },
  "mospi.gov.in":                  { score: 92, label: "Government Statistics" },
  "msf.org":                       { score: 92, label: "Humanitarian Organization" },
  "northwestern.edu":              { score: 92, label: "Academic Institution" },
  "nus.edu.sg":                    { score: 92, label: "Academic Institution" },
  "osce.org":                      { score: 92, label: "International Organization" },
  "pmo.gov.in":                    { score: 92, label: "Government Source" },
  "presidentofindia.gov.in":       { score: 92, label: "Government Source" },
  "rajyasabha.nic.in":             { score: 92, label: "Legislative Source" },
  "tokyo.ac.jp":                   { score: 92, label: "Academic Institution" },
  "uchicago.edu":                  { score: 92, label: "Academic Institution" },
  "ucl.ac.uk":                     { score: 92, label: "Academic Institution" },
  "ucla.edu":                      { score: 92, label: "Academic Institution" },
  "uidai.gov.in":                  { score: 92, label: "Government Authority" },
  "umich.edu":                     { score: 92, label: "Academic Institution" },
  "unfccc.int":                    { score: 92, label: "International Organization" },
  "upenn.edu":                     { score: 92, label: "Academic Institution" },
  "nytimes.com":                   { score: 91, label: "Major National Newspaper" },
  "afpfactcheck.com":              { score: 90, label: "Fact-Checker" },
  "apa.org":                       { score: 90, label: "Professional Organization" },
  "bbc.co.uk":                     { score: 90, label: "Public Broadcaster" },
  "bbc.com":                       { score: 90, label: "Public Broadcaster" },
  "crossref.org":                  { score: 90, label: "Research Infrastructure" },
  "ddnews.gov.in":                 { score: 90, label: "Public Broadcaster" },
  "digitalindia.gov.in":           { score: 90, label: "Government Programme" },
  "doi.org":                       { score: 90, label: "Research Identifier" },
  "ed.ac.uk":                      { score: 90, label: "Academic Institution" },
  "factcheck.afp.com":             { score: 90, label: "Fact-Checker" },
  "ieee.org":                      { score: 90, label: "Professional Organization" },
  "iitb.ac.in":                    { score: 90, label: "Academic Institution" },
  "iitd.ac.in":                    { score: 90, label: "Academic Institution" },
  "kcl.ac.uk":                     { score: 90, label: "Academic Institution" },
  "lawcommissionofindia.nic.in":   { score: 90, label: "Legal Research Institution" },
  "loksabhatv.nic.in":             { score: 90, label: "Public Broadcaster" },
  "manchester.ac.uk":              { score: 90, label: "Academic Institution" },
  "mygov.in":                      { score: 90, label: "Government Source" },
  "nato.int":                      { score: 90, label: "International Organization" },
  "niti.gov.in":                   { score: 90, label: "Government Policy Institution" },
  "ntu.edu.sg":                    { score: 90, label: "Academic Institution" },
  "pewresearch.org":               { score: 90, label: "Research Organization" },
  "propublica.org":                { score: 90, label: "Investigative Journalism" },
  "rajyasabhatv.nic.in":           { score: 90, label: "Public Broadcaster" },
  "sansadtv.nic.in":               { score: 90, label: "Public Broadcaster" },
  "snopes.com":                    { score: 90, label: "Fact-Checker" },
  "tifr.res.in":                   { score: 90, label: "Research Institution" },
  "tudelft.nl":                    { score: 90, label: "Academic Institution" },
  "upi.com":                       { score: 90, label: "International Wire Service" },
  "washingtonpost.com":            { score: 90, label: "Major National Newspaper" },
  "whitehouse.gov":                { score: 90, label: "Government Source" },
  "wsj.com":                       { score: 90, label: "Major National Newspaper" },
  "theguardian.com":               { score: 89, label: "Major National Newspaper" },
  "airnewsalerts.com":             { score: 88, label: "Public Broadcaster" },
  "ansa.it":                       { score: 88, label: "National News Agency" },
  "britannica.com":                { score: 88, label: "Encyclopedia" },
  "c-span.org":                    { score: 88, label: "Public Affairs Broadcaster" },
  "dpa.com":                       { score: 88, label: "International News Agency" },
  "efe.com":                       { score: 88, label: "International News Agency" },
  "factcheck.politifact.com":      { score: 88, label: "Fact-Checker" },
  "fullfact.org":                  { score: 88, label: "Fact-Checker" },
  "gallup.com":                    { score: 88, label: "Polling Organization" },
  "hopkinsmedicine.org":           { score: 88, label: "Medical Institution" },
  "iiit.ac.in":                    { score: 88, label: "Academic Institution" },
  "jstor.org":                     { score: 88, label: "Academic Archive" },
  "kyodonews.net":                 { score: 88, label: "International News Agency" },
  "lemonde.fr":                    { score: 88, label: "Major National Newspaper" },
  "mayoclinic.org":                { score: 88, label: "Medical Institution" },
  "newyorker.com":                 { score: 88, label: "Premium News Magazine" },
  "nhk.jp":                        { score: 88, label: "Public Broadcaster" },
  "nhk.or.jp":                     { score: 88, label: "Public Broadcaster" },
  "npr.org":                       { score: 88, label: "Public Radio" },
  "ourworldindata.org":            { score: 88, label: "Data Research Organization" },
  "pbs.org":                       { score: 88, label: "Public Broadcaster" },
  "politifact.com":                { score: 88, label: "Fact-Checker" },
  "prsindia.org":                  { score: 88, label: "Legislative Research Organization" },
  "ptinews.com":                   { score: 88, label: "Indian News Agency" },
  "scientificamerican.com":        { score: 88, label: "Science Magazine" },
  "spectrum.ieee.org":             { score: 88, label: "Technology News" },
  "spiegel.de":                    { score: 88, label: "Major National Newspaper" },
  "abc.net.au":                    { score: 87, label: "Public Broadcaster" },
  "boomlive.in":                   { score: 87, label: "Fact-Checker" },
  "cbc.ca":                        { score: 87, label: "Public Broadcaster" },
  "dw.com":                        { score: 87, label: "Public Broadcaster" },
  "theatlantic.com":               { score: 87, label: "Premium News Magazine" },
  "apa.at":                        { score: 86, label: "National News Agency" },
  "ard.de":                        { score: 86, label: "Public Broadcaster" },
  "ats.ch":                        { score: 86, label: "National News Agency" },
  "belga.be":                      { score: 86, label: "National News Agency" },
  "clevelandclinic.org":           { score: 86, label: "Medical Institution" },
  "dpa-factchecking.com":          { score: 86, label: "Fact-Checker" },
  "keystone-sda.ch":               { score: 86, label: "National News Agency" },
  "nationalgeographic.com":        { score: 86, label: "Science/Culture Publisher" },
  "nikkei.com":                    { score: 86, label: "Financial Newspaper" },
  "nrk.no":                        { score: 86, label: "Public Broadcaster" },
  "smithsonianmag.com":            { score: 86, label: "Science/Culture Publisher" },
  "tagesschau.de":                 { score: 86, label: "Public Broadcaster" },
  "technologyreview.com":          { score: 86, label: "Technology Magazine" },
  "yonhapnews.co.kr":              { score: 86, label: "National News Agency" },
  "zdf.de":                        { score: 86, label: "Public Broadcaster" },
  "arstechnica.com":               { score: 85, label: "Technology News" },
  "dr.dk":                         { score: 85, label: "Public Broadcaster" },
  "elpais.com":                    { score: 85, label: "Major National Newspaper" },
  "france24.com":                  { score: 85, label: "Public Broadcaster" },
  "jiji.com":                      { score: 85, label: "Japanese News Agency" },
  "scmp.com":                      { score: 85, label: "Major National Newspaper" },
  "straitstimes.com":              { score: 85, label: "Major National Newspaper" },
  "svt.se":                        { score: 85, label: "Public Broadcaster" },
  "thehindu.com":                  { score: 85, label: "Major National Newspaper" },
  "wdr.de":                        { score: 85, label: "Public Broadcaster" },
  "yle.fi":                        { score: 85, label: "Public Broadcaster" },
  "aap.com.au":                    { score: 84, label: "Fact-Checker" },
  "africacheck.org":               { score: 84, label: "Fact-Checker" },
  "aljazeera.com":                 { score: 84, label: "International Broadcaster" },
  "aljazeera.net":                 { score: 84, label: "International Broadcaster" },
  "altnews.in":                    { score: 84, label: "Fact-Checker" },
  "asahi.com":                     { score: 84, label: "Major National Newspaper" },
  "channelnewsasia.com":           { score: 84, label: "Major Broadcaster" },
  "christiansciencemonitor.com":   { score: 84, label: "News Organization" },
  "cnn.com":                       { score: 84, label: "Major Broadcaster" },
  "correctiv.org":                 { score: 84, label: "Fact-Checker" },
  "csmonitor.com":                 { score: 84, label: "News Organization" },
  "deutschlandfunk.de":            { score: 84, label: "Public Radio" },
  "faz.net":                       { score: 84, label: "Major National Newspaper" },
  "foreignaffairs.com":            { score: 84, label: "International Affairs" },
  "globeandmail.com":              { score: 84, label: "Major National Newspaper" },
  "ilsole24ore.com":               { score: 84, label: "Financial Newspaper" },
  "kbs.co.kr":                     { score: 84, label: "Public Broadcaster" },
  "lesdecodeurs.blog.lemonde.fr":  { score: 84, label: "Fact-Checker" },
  "lusa.pt":                       { score: 84, label: "National News Agency" },
  "maldita.es":                    { score: 84, label: "Fact-Checker" },
  "newscientist.com":              { score: 84, label: "Science Magazine" },
  "newtral.es":                    { score: 84, label: "Fact-Checker" },
  "nrc.nl":                        { score: 84, label: "Major National Newspaper" },
  "nzz.ch":                        { score: 84, label: "Major National Newspaper" },
  "orf.at":                        { score: 84, label: "Public Broadcaster" },
  "rai.it":                        { score: 84, label: "Public Broadcaster" },
  "rainews.it":                    { score: 84, label: "Public Broadcaster" },
  "sbs.com.au":                    { score: 84, label: "Public Broadcaster" },
  "srf.ch":                        { score: 84, label: "Public Broadcaster" },
  "sueddeutsche.de":               { score: 84, label: "Major National Newspaper" },
  "thetimes.co.uk":                { score: 84, label: "Major National Newspaper" },
  "zeit.de":                       { score: 84, label: "Major National Newspaper" },
  "indianexpress.com":             { score: 83, label: "Major National Newspaper" },
  "rtve.es":                       { score: 83, label: "Public Broadcaster" },
  "abcnews.go.com":                { score: 82, label: "Major Broadcaster" },
  "aninews.in":                    { score: 82, label: "Indian News Agency" },
  "arxiv.org":                     { score: 82, label: "Research Repository" },
  "bostonglobe.com":               { score: 82, label: "Major National Newspaper" },
  "cbsnews.com":                   { score: 82, label: "Major Broadcaster" },
  "corriere.it":                   { score: 82, label: "Major National Newspaper" },
  "dubawa.org":                    { score: 82, label: "Fact-Checker" },
  "espn.com":                      { score: 82, label: "Sports News" },
  "espncricinfo.com":              { score: 82, label: "Sports News" },
  "factchecker.in":                { score: 82, label: "Fact-Checker" },
  "handelsblatt.com":              { score: 82, label: "Financial News" },
  "japantimes.co.jp":              { score: 82, label: "Major National Newspaper" },
  "latimes.com":                   { score: 82, label: "Major National Newspaper" },
  "lefigaro.fr":                   { score: 82, label: "Major National Newspaper" },
  "lesechos.fr":                   { score: 82, label: "Financial Newspaper" },
  "mainichi.jp":                   { score: 82, label: "Major National Newspaper" },
  "mimikama.org":                  { score: 82, label: "Fact-Checker" },
  "nbcnews.com":                   { score: 82, label: "Major Broadcaster" },
  "nos.nl":                        { score: 82, label: "Public Broadcaster" },
  "pagellapolitica.it":            { score: 82, label: "Fact-Checker" },
  "rfi.fr":                        { score: 82, label: "Public Radio" },
  "rsi.ch":                        { score: 82, label: "Public Broadcaster" },
  "rtbf.be":                       { score: 82, label: "Public Broadcaster" },
  "rtp.pt":                        { score: 82, label: "Public Broadcaster" },
  "rts.ch":                        { score: 82, label: "Public Broadcaster" },
  "smh.com.au":                    { score: 82, label: "Major National Newspaper" },
  "spacenews.com":                 { score: 82, label: "Space News" },
  "swissinfo.ch":                  { score: 82, label: "Public Broadcaster" },
  "telegraph.co.uk":               { score: 82, label: "Major National Newspaper" },
  "theage.com.au":                 { score: 82, label: "Major National Newspaper" },
  "time.com":                      { score: 82, label: "News Magazine" },
  "tv2.dk":                        { score: 82, label: "Broadcaster" },
  "tv2.no":                        { score: 82, label: "Broadcaster" },
  "tve.es":                        { score: 82, label: "Public Broadcaster" },
  "wired.com":                     { score: 82, label: "Technology News" },
  "yomiuri.co.jp":                 { score: 82, label: "Major National Newspaper" },
  "aftenposten.no":                { score: 80, label: "Major National Newspaper" },
  "al-monitor.com":                { score: 80, label: "Middle East News" },
  "barrons.com":                   { score: 80, label: "Financial News" },
  "brisbanetimes.com.au":          { score: 80, label: "Major National Newspaper" },
  "channel4.com":                  { score: 80, label: "Broadcaster" },
  "cnbc.com":                      { score: 80, label: "Financial News" },
  "dagensnyheter.se":              { score: 80, label: "Major National Newspaper" },
  "derstandard.at":                { score: 80, label: "Major National Newspaper" },
  "dn.se":                         { score: 80, label: "Major National Newspaper" },
  "facta.news":                    { score: 80, label: "Fact-Checker" },
  "factly.in":                     { score: 80, label: "Fact-Checker" },
  "fortune.com":                   { score: 80, label: "Business News" },
  "haaretz.com":                   { score: 80, label: "Major National Newspaper" },
  "lavanguardia.com":              { score: 80, label: "Major National Newspaper" },
  "leadstories.com":               { score: 80, label: "Fact-Checker" },
  "logically.ai":                  { score: 80, label: "Fact-Checker" },
  "repubblica.it":                 { score: 80, label: "Major National Newspaper" },
  "sabcnews.com":                  { score: 80, label: "Public Broadcaster" },
  "seattletimes.com":              { score: 80, label: "Major National Newspaper" },
  "sfchronicle.com":               { score: 80, label: "Major National Newspaper" },
  "skysports.com":                 { score: 80, label: "Sports News" },
  "startribune.com":               { score: 80, label: "Major National Newspaper" },
  "valor.globo.com":               { score: 80, label: "Financial News" },
  "chicagotribune.com":            { score: 79, label: "Major National Newspaper" },
  "euronews.com":                  { score: 79, label: "European Broadcaster" },
  "independent.co.uk":             { score: 79, label: "Major National Newspaper" },
  "scroll.in":                     { score: 79, label: "Independent News" },
  "theverge.com":                  { score: 79, label: "Technology News" },
  "thewire.in":                    { score: 79, label: "Independent News" },
  "vox.com":                       { score: 79, label: "News and Analysis" },
  "abc.es":                        { score: 78, label: "Major National Newspaper" },
  "anandtech.com":                 { score: 78, label: "Technology News" },
  "axios.com":                     { score: 78, label: "Digital News" },
  "canberratimes.com.au":          { score: 78, label: "Major National Newspaper" },
  "commons.wikimedia.org":         { score: 78, label: "Encyclopedia" },
  "ctvnews.ca":                    { score: 78, label: "Major Broadcaster" },
  "dailymaverick.co.za":           { score: 78, label: "Independent News" },
  "dallasnews.com":                { score: 78, label: "Major National Newspaper" },
  "diepresse.com":                 { score: 78, label: "Major National Newspaper" },
  "elmundo.es":                    { score: 78, label: "Major National Newspaper" },
  "estadao.com.br":                { score: 78, label: "Major National Newspaper" },
  "expresso.pt":                   { score: 78, label: "Major National Newspaper" },
  "factcheck.ge":                  { score: 78, label: "Fact-Checker" },
  "folha.uol.com.br":              { score: 78, label: "Major National Newspaper" },
  "foreignpolicy.com":             { score: 78, label: "International Affairs" },
  "globalnews.ca":                 { score: 78, label: "Major Broadcaster" },
  "helsinginsanomat.fi":           { score: 78, label: "Major National Newspaper" },
  "houstonchronicle.com":          { score: 78, label: "Major National Newspaper" },
  "indiatoday.in":                 { score: 78, label: "Major News Portal" },
  "inquirer.com":                  { score: 78, label: "Major National Newspaper" },
  "itv.com":                       { score: 78, label: "Broadcaster" },
  "koreaherald.com":               { score: 78, label: "Major National Newspaper" },
  "koreatimes.co.kr":              { score: 78, label: "Major National Newspaper" },
  "kyivindependent.com":           { score: 78, label: "Independent News" },
  "lanacion.com.ar":               { score: 78, label: "Major National Newspaper" },
  "lastampa.it":                   { score: 78, label: "Major National Newspaper" },
  "letemps.ch":                    { score: 78, label: "Major National Newspaper" },
  "liberation.fr":                 { score: 78, label: "Major National Newspaper" },
  "livemint.com":                  { score: 78, label: "Financial News" },
  "miamiherald.com":               { score: 78, label: "Major National Newspaper" },
  "money.cnn.com":                 { score: 78, label: "Financial News" },
  "ndtv.com":                      { score: 78, label: "Major Broadcaster" },
  "oglobo.globo.com":              { score: 78, label: "Major National Newspaper" },
  "ouest-france.fr":               { score: 78, label: "Major National Newspaper" },
  "phys.org":                      { score: 78, label: "Science News" },
  "politiken.dk":                  { score: 78, label: "Major National Newspaper" },
  "publico.pt":                    { score: 78, label: "Major National Newspaper" },
  "sciencedaily.com":              { score: 78, label: "Science News" },
  "spaceflightnow.com":            { score: 78, label: "Space News" },
  "statista.com":                  { score: 78, label: "Data Publisher" },
  "svd.se":                        { score: 78, label: "Major National Newspaper" },
  "tagesanzeiger.ch":              { score: 78, label: "Major National Newspaper" },
  "techcrunch.com":                { score: 78, label: "Technology News" },
  "theaustralian.com.au":          { score: 78, label: "Major National Newspaper" },
  "theintercept.com":              { score: 78, label: "Investigative Journalism" },
  "thestar.com":                   { score: 78, label: "Major National Newspaper" },
  "timesofisrael.com":             { score: 78, label: "Major News Portal" },
  "ukrinform.net":                 { score: 78, label: "National News Agency" },
  "usatoday.com":                  { score: 78, label: "Major National Newspaper" },
  "vishvasnews.com":               { score: 78, label: "Fact-Checker" },
  "volkskrant.nl":                 { score: 78, label: "Major National Newspaper" },
  "watoday.com.au":                { score: 78, label: "Major National Newspaper" },
  "wikimedia.org":                 { score: 78, label: "Encyclopedia" },
  "wikipedia.org":                 { score: 78, label: "Encyclopedia" },
  "9news.com.au":                  { score: 76, label: "Broadcaster" },
  "ajc.com":                       { score: 76, label: "Major National Newspaper" },
  "americanbanker.com":            { score: 76, label: "Financial News" },
  "berlingske.dk":                 { score: 76, label: "Major National Newspaper" },
  "business-standard.com":         { score: 76, label: "Financial News" },
  "calgaryherald.com":             { score: 76, label: "Major National Newspaper" },
  "clarin.com":                    { score: 76, label: "Major National Newspaper" },
  "deccanherald.com":              { score: 76, label: "Major National Newspaper" },
  "denverpost.com":                { score: 76, label: "Major National Newspaper" },
  "discovermagazine.com":          { score: 76, label: "Science Magazine" },
  "dn.pt":                         { score: 76, label: "Major National Newspaper" },
  "economictimes.indiatimes.com":  { score: 76, label: "Financial News" },
  "edmontonjournal.com":           { score: 76, label: "Major National Newspaper" },
  "eldiario.es":                   { score: 76, label: "Digital News" },
  "ewn.co.za":                     { score: 76, label: "News Broadcaster" },
  "financialexpress.com":          { score: 76, label: "Financial News" },
  "forbes.com":                    { score: 76, label: "Business News" },
  "ilpost.it":                     { score: 76, label: "Digital News" },
  "interfax.com.ua":               { score: 76, label: "News Agency" },
  "jpost.com":                     { score: 76, label: "Major National Newspaper" },
  "jyllands-posten.dk":            { score: 76, label: "Major National Newspaper" },
  "kurier.at":                     { score: 76, label: "Major National Newspaper" },
  "mailandguardian.co.za":         { score: 76, label: "Major National Newspaper" },
  "marketwatch.com":               { score: 76, label: "Financial News" },
  "meduza.io":                     { score: 76, label: "Independent News" },
  "mg.co.za":                      { score: 76, label: "Major National Newspaper" },
  "moneycontrol.com":              { score: 76, label: "Financial News" },
  "montrealgazette.com":           { score: 76, label: "Major National Newspaper" },
  "motherjones.com":               { score: 76, label: "Investigative Journalism" },
  "n-tv.de":                       { score: 76, label: "Broadcaster" },
  "news24.com":                    { score: 76, label: "Major News Portal" },
  "oregonian.com":                 { score: 76, label: "Regional Newspaper" },
  "oregonlive.com":                { score: 76, label: "Regional Newspaper" },
  "ottawacitizen.com":             { score: 76, label: "Major National Newspaper" },
  "politico.com":                  { score: 76, label: "Political News" },
  "premiumtimesng.com":            { score: 76, label: "Independent News" },
  "sky.com":                       { score: 76, label: "Broadcaster" },
  "skynews.com":                   { score: 76, label: "Broadcaster" },
  "space.com":                     { score: 76, label: "Science News" },
  "ssrn.com":                      { score: 76, label: "Research Repository" },
  "tampabay.com":                  { score: 76, label: "Major National Newspaper" },
  "taz.de":                        { score: 76, label: "Major National Newspaper" },
  "theafricareport.com":           { score: 76, label: "African News" },
  "thehindubusinessline.com":      { score: 76, label: "Financial News" },
  "themoscowtimes.com":            { score: 76, label: "Independent News" },
  "theprint.in":                   { score: 76, label: "Independent News" },
  "thequint.com":                  { score: 76, label: "Digital News" },
  "todayonline.com":               { score: 76, label: "Major News Portal" },
  "trouw.nl":                      { score: 76, label: "Major National Newspaper" },
  "vancouversun.com":              { score: 76, label: "Major National Newspaper" },
  "cleveland.com":                 { score: 75, label: "Regional News" },
  "dawn.com":                      { score: 75, label: "Major National Newspaper" },
  "hindustantimes.com":            { score: 75, label: "Major National Newspaper" },
  "jsonline.com":                  { score: 75, label: "Regional Newspaper" },
  "newslaundry.com":               { score: 75, label: "Digital News" },
  "sacbee.com":                    { score: 75, label: "Regional Newspaper" },
  "sltrib.com":                    { score: 75, label: "Regional Newspaper" },
  "timesofindia.indiatimes.com":   { score: 75, label: "Major National Newspaper" },
  "7news.com.au":                  { score: 74, label: "Broadcaster" },
  "aajtak.in":                     { score: 74, label: "Major Broadcaster" },
  "accountingtoday.com":           { score: 74, label: "Financial News" },
  "africanews.com":                { score: 74, label: "Pan-African Broadcaster" },
  "baltimoresun.com":              { score: 74, label: "Regional Newspaper" },
  "bdnews24.com":                  { score: 74, label: "Digital News" },
  "brecorder.com":                 { score: 74, label: "Financial News" },
  "businessday.ng":                { score: 74, label: "Financial News" },
  "checkyourfact.com":             { score: 74, label: "Fact-Checker" },
  "courant.com":                   { score: 74, label: "Regional Newspaper" },
  "cricbuzz.com":                  { score: 74, label: "Sports News" },
  "dispatch.com":                  { score: 74, label: "Regional Newspaper" },
  "engadget.com":                  { score: 74, label: "Technology News" },
  "guardian.ng":                   { score: 74, label: "Major National Newspaper" },
  "history.com":                   { score: 74, label: "History Publisher" },
  "japantoday.com":                { score: 74, label: "News Portal" },
  "jordantimes.com":               { score: 74, label: "National Newspaper" },
  "kathmandupost.com":             { score: 74, label: "Major National Newspaper" },
  "middleeasteye.net":             { score: 74, label: "Regional News" },
  "newindianexpress.com":          { score: 74, label: "Major National Newspaper" },
  "news.abplive.com":              { score: 74, label: "Major Broadcaster" },
  "news18.com":                    { score: 74, label: "Major News Portal" },
  "newsfirst.lk":                  { score: 74, label: "Broadcaster" },
  "popularmechanics.com":          { score: 74, label: "Science/Technology Magazine" },
  "record.pt":                     { score: 74, label: "Sports News" },
};

// ─────────────────────────────────────────────────────────────────────────────
// Utility helpers
// ─────────────────────────────────────────────────────────────────────────────

export function lookupDomain(domain: string): { score: number; label: string } | null {
  return CREDIBLE_SOURCES[domain] ?? null;
}

export function isDomainCredible(domain: string): boolean {
  const entry = CREDIBLE_SOURCES[domain];
  return !!entry && entry.score >= CREDIBILITY_THRESHOLD;
}

export function getNodeColor(domain: string): string {
  return isDomainCredible(domain) ? '#22c55e' : '#ef4444';
}

// ─────────────────────────────────────────────────────────────────────────────
// Graph node/link types
// ─────────────────────────────────────────────────────────────────────────────

export interface GraphNodeData {
  id: number;
  label: string;
  domain: string;
  url?: string;
  val: number;
  color: string;
  isSource: boolean;
  credScore: number | null;
  credLabel: string;
  x?: number;
  y?: number;
}

export interface GraphLinkData {
  source: number;
  target: number;
  color: string;
}

export interface PropagationGraphData {
  nodes: GraphNodeData[];
  links: GraphLinkData[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Synthetic source pools for graph generation when backend doesn't supply URLs
// ─────────────────────────────────────────────────────────────────────────────

const HIGH_CRED_POOL = [
  'reuters.com', 'apnews.com', 'bbc.com', 'nytimes.com', 'theguardian.com',
  'washingtonpost.com', 'bloomberg.com', 'wsj.com', 'ft.com', 'economist.com',
  'bbc.co.uk', 'npr.org', 'afp.com', 'factcheck.org', 'snopes.com',
];

const MID_CRED_POOL = [
  'cnn.com', 'nbcnews.com', 'cbsnews.com', 'abcnews.go.com', 'theatlantic.com',
  'axios.com', 'politico.com', 'vox.com', 'wired.com', 'techcrunch.com',
  'nationalgeographic.com', 'scientificamerican.com', 'time.com', 'cnbc.com',
];

const LOW_CRED_POOL = [
  'unverified-reports.net', 'viral-news-central.com', 'clickbait-daily.org',
  'biased-media.net', 'sensational-post.com',
];

/**
 * Builds a force-graph dataset from a CredibilityScorecard.
 * Uses `sources_used` if the backend provides them;
 * otherwise falls back to a deterministic synthetic graph.
 */
export function buildGraphFromScorecard(sc: CredibilityScorecard): PropagationGraphData {
  const mainDomain = sc.domain ?? 'unknown-source.com';
  const mainEntry  = CREDIBLE_SOURCES[mainDomain];
  const mainColor  = mainEntry && mainEntry.score >= CREDIBILITY_THRESHOLD ? '#22c55e' : '#ef4444';

  const nodes: GraphNodeData[] = [{
    id:        0,
    label:     mainDomain,
    domain:    mainDomain,
    val:       10,
    color:     mainColor,
    isSource:  true,
    credScore: mainEntry?.score ?? null,
    credLabel: mainEntry?.label ?? 'Unknown Source',
  }];

  // ── If backend supplies explicit sources, use them ───────────────────────
  if (sc.corroboration?.top_sources && sc.corroboration.top_sources.length > 0) {
    sc.corroboration.top_sources.slice(0, 14).forEach((s, i) => {
      const e   = CREDIBLE_SOURCES[s.domain];
      const col = s.trusted ? '#22c55e' : '#ef4444';
      nodes.push({
        id:        i + 1,
        label:     s.domain,
        domain:    s.domain,
        url:       s.url,
        val:       s.trusted ? 4 : 3,
        color:     col,
        isSource:  false,
        credScore: e?.score ?? null,
        credLabel: e?.label ?? 'Unknown',
      });
    });
  } else {
    // ── Synthetic generation ─────────────────────────────────────────────
    const score = sc.overall_score;
    let pool: string[];

    if (score >= 70) {
      pool = [
        ...HIGH_CRED_POOL.slice(0, 7),
        ...MID_CRED_POOL.slice(0, 4),
        ...LOW_CRED_POOL.slice(0, 2),
      ];
    } else if (score >= 45) {
      pool = [
        ...HIGH_CRED_POOL.slice(0, 4),
        ...MID_CRED_POOL.slice(0, 4),
        ...LOW_CRED_POOL.slice(0, 4),
      ];
    } else {
      pool = [
        ...HIGH_CRED_POOL.slice(0, 2),
        ...MID_CRED_POOL.slice(0, 3),
        ...LOW_CRED_POOL,
      ];
    }

    // Remove the article domain from pool to avoid duplicate
    const filtered = pool.filter(d => d !== mainDomain).slice(0, 13);
    filtered.forEach((domain, i) => {
      const e          = CREDIBLE_SOURCES[domain];
      const isCredible = !!e && e.score >= CREDIBILITY_THRESHOLD;
      nodes.push({
        id:        i + 1,
        label:     domain,
        domain,
        val:       isCredible ? 4 : 3,
        color:     isCredible ? '#22c55e' : '#ef4444',
        isSource:  false,
        credScore: e?.score ?? null,
        credLabel: e?.label ?? 'Unverified Source',
      });
    });
  }

  // ── Build links (BA-like topology) ──────────────────────────────────────
  const links: GraphLinkData[] = [];
  const directSpokes = Math.min(5, nodes.length - 1);

  // Hub-and-spoke from source → first N nodes
  for (let i = 1; i <= directSpokes; i++) {
    links.push({ source: 0, target: i, color: 'rgba(180,180,180,0.25)' });
  }

  // Secondary edges (deterministic, avoids Math.random for reproducibility)
  for (let i = directSpokes + 1; i < nodes.length; i++) {
    const base = ((i * 3) % directSpokes) + 1;
    links.push({ source: base, target: i, color: 'rgba(180,180,180,0.15)' });
    // Occasional cross-link for richer topology
    if (i % 3 === 0 && i > 2) {
      links.push({ source: i - 2, target: i, color: 'rgba(180,180,180,0.10)' });
    }
  }

  return { nodes, links };
}
