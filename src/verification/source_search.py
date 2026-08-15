
"""
WebCorroborator: Uses Tavily to search for corroborating news articles
from trusted sources on the internet, then scrapes and scores their content
using trafilatura for clean text extraction.
"""

import urllib.parse
import logging
from typing import List, Dict, Any, Optional

import trafilatura
from tavily import TavilyClient

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Curated master list of globally trusted news and fact-checking domains
TRUSTED_DOMAINS = {
    # ── International Wire Services ──────────────────────────────────────────
    "reuters.com", "apnews.com", "afp.com", "bloomberg.com", "upi.com",
    "ansa.it", "dpa.com", "efe.com", "kyodonews.net", "yonhapnews.co.kr",

    # ── Major International / National Newspapers ────────────────────────────
    "nytimes.com", "washingtonpost.com", "theguardian.com", "wsj.com", "ft.com",
    "economist.com", "bbc.com", "bbc.co.uk", "theatlantic.com", "newyorker.com",
    "time.com", "newsweek.com", "lemonde.fr", "spiegel.de", "sueddeutsche.de",
    "thetimes.co.uk", "telegraph.co.uk", "independent.co.uk", "thesun.co.uk",
    "abc.es", "elmundo.es", "elpais.com", "lavanguardia.com", "larazon.es",
    "lefigaro.fr", "liberation.fr", "ledevoir.com", "lapresse.ca", "globeandmail.com",
    "nationalpost.com", "thestar.com", "ottawacitizen.com", "montrealgazette.com",
    "smh.com.au", "theage.com.au", "abc.net.au", "sbs.com.au", "theaustralian.com.au",
    "japantimes.co.jp", "asahi.com", "mainichi.jp", "yomiuri.co.jp", "nikkei.com",
    "koreaherald.com", "koreatimes.co.kr", "scmp.com", "straitstimes.com",
    "haaretz.com", "jpost.com", "timesofisrael.com", "thetimes.co.uk",
    "dawn.com", "thehindu.com", "hindustantimes.com", "timesofindia.indiatimes.com",
    "ndtv.com", "indianexpress.com", "livemint.com", "business-standard.com",
    "deccanherald.com", "scroll.in", "thewire.in", "theprint.in", "thequint.com",
    "aljazeera.com", "aljazeera.net", "middleeasteye.net", "al-monitor.com",
    "bostonglobe.com", "latimes.com", "chicagotribune.com", "seattletimes.com",
    "dallasnews.com", "houstonchronicle.com", "sfchronicle.com", "tampabay.com",
    "denverpost.com", "baltimoresun.com", "startribune.com", "oregonlive.com",
    "miamiherald.com", "ajc.com", "azcentral.com", "sacbee.com", "statesman.com",
    "bostonherald.com", "nypost.com", "nydailynews.com", "sfgate.com",
    "deseret.com", "sltrib.com", "freep.com", "jsonline.com", "oregonian.com",
    "courier-journal.com", "tennessean.com", "cincinnati.com", "dispatch.com",
    "post-gazette.com", "triblive.com", "mercurynews.com", "eastbaytimes.com",
    "dw.com", "france24.com", "euronews.com", "rte.ie", "irishtimes.com",
    "heraldscotland.com", "walesonline.co.uk", "yle.fi", "svt.se", "dr.dk",
    "nrk.no", "hs.fi", "aftenposten.no", "derstandard.at", "diepresse.com",
    "zeit.de", "faz.net", "welt.de", "taz.de", "handelsblatt.com",
    "corriere.it", "repubblica.it", "lastampa.it", "ilpost.it",
    "volkskrant.nl", "nos.nl", "nrc.nl", "ad.nl", "hln.be",
    "digi24.ro", "novinky.cz", "delo.si", "indexmundi.com",

    # ── Public Broadcasters ───────────────────────────────────────────────────
    "npr.org", "pbs.org", "cbc.ca", "radio-canada.ca", "rtve.es",
    "rfi.fr", "voanews.com", "rferl.org", "nhk.or.jp", "nhk.jp",
    "kbs.co.kr", "arirang.com", "zdf.de", "ard.de", "wdr.de",
    "orf.at", "rai.it", "rainews.it", "rtbf.be", "srf.ch", "rts.ch",
    "nrk.no", "svt.se", "yle.fi", "dr.dk", "tv2.dk", "tv2.no",
    "cp24.com", "ctvnews.ca", "globalnews.ca",
    "ddnews.gov.in", "airnewsalerts.com",

    # ── Major US Broadcast Networks ───────────────────────────────────────────
    "cbsnews.com", "nbcnews.com", "abcnews.go.com", "cnn.com", "foxnews.com",
    "msnbc.com", "cnbc.com", "abc7news.com", "abc7chicago.com", "abc7ny.com",
    "abc11.com", "abc12.com", "abc13.com", "abc30.com", "6abc.com",
    "abcnews4.com", "abc27.com", "abc3340.com", "actionnewsjax.com",
    "abc4.com", "abc17news.com", "azfamily.com", "katu.com", "katv.com",
    "kaaltv.com", "kait8.com", "kalb.com", "kark.com", "kbtx.com",
    "kcbd.com", "kcci.com", "kcentv.com", "kcrg.com", "kctv5.com",
    "kdvr.com", "keloland.com", "kens5.com", "ketk.com", "keyt.com",
    "kezi.com", "kfvs12.com", "kgns.tv", "kgw.com", "khou.com",
    "khon2.com", "khqa.com", "kimt.com", "kion546.com", "kiro7.com",
    "kitv.com", "kivitv.com", "kktv.com", "kltv.com", "kmbc.com",
    "kmov.com", "knoe.com", "koaa.com", "koamnewsnow.com", "koat.com",
    "kob.com", "koin.com", "kold.com", "kolotv.com", "komonews.com",
    "kplctv.com", "kptv.com", "kpvi.com", "krdo.com", "krem.com",
    "kron4.com", "krqe.com", "krtv.com", "ksat.com", "ksdk.com",
    "ksla.com", "ksn.com", "kstp.com", "kswo.com", "ktnv.com",
    "ktla.com", "ktul.com", "ktvb.com", "ktiv.com", "ktre.com",
    "ktsm.com", "ktvq.com", "ktvz.com", "ktvu.com", "kvia.com",
    "kvoa.com", "kvue.com", "kwch.com", "kwtx.com", "kwwl.com",
    "kxan.com", "kxii.com", "kxly.com", "kxxv.com", "kyma.com",
    "ky3.com", "king5.com", "kpic.com", "kqed.org", "kslnews.com",
    "ksl.com", "ksdk.com", "4029tv.com",
    "nbcchicago.com", "nbcdfw.com", "nbclosangeles.com", "nbcmiami.com",
    "nbcnews.com", "nbcnewyork.com", "nbcphiladelphia.com", "nbcwashington.com",
    "nbcboston.com", "nbcmontana.com",
    "newyork.cbslocal.com", "seattle.cbslocal.com", "chicago.cbslocal.com",
    "atlanta.cbslocal.com", "miami.cbslocal.com", "minnesota.cbslocal.com",
    "philadelphia.cbslocal.com", "denver.cbslocal.com", "sanfrancisco.cbslocal.com",
    "sacramento.cbslocal.com", "tampa.cbslocal.com", "detroit.cbslocal.com",
    "newyork.cbslocal.com", "los-angeles.cbslocal.com",
    "wral.com", "wsbtv.com", "wsoctv.com", "wtae.com", "wthr.com",
    "wtvd.com", "wtvj.com", "wusa9.com", "wvtm13.com", "wxyz.com",
    "wyff4.com", "wzzm13.com", "11alive.com", "wxii12.com",
    "wkrg.com", "wlbt.com", "wlfi.com", "wlky.com", "wlox.com",
    "wltx.com", "wmar2news.com", "wnem.com", "wnyt.com", "wowktv.com",
    "wowt.com", "wpbf.com", "wpxi.com", "wrbw.com", "wreg.com",
    "wric.com", "wsav.com", "wsfa.com", "wsmv.com", "wtvr.com",
    "wtvm.com", "wtvy.com", "wvlt.tv", "thv11.com", "13wmaz.com",
    "nbc4i.com", "wcnc.com", "live5news.com", "wctv.tv", "wdam.com",
    "wdbj7.com", "wdio.com", "wdsu.com", "wdtn.com", "wdtv.com",
    "wect.com", "wesh.com", "wfla.com", "wfmz.com", "wfmynews2.com",
    "wftv.com", "wgntv.com", "whas11.com", "whio.com", "whnt.com",
    "who13.com", "whsv.com", "wicz.com", "wilx.com", "winknews.com",
    "wistv.com", "witn.com", "wivb.com", "wjbf.com", "wjcl.com",
    "wjhg.com", "wjhl.com", "wjtv.com", "wkbn.com", "wkbw.com",
    "wkow.com", "wlns.com", "wnct.com", "wndu.com", "wcvb.com",
    "wbaltv.com", "wbay.com", "wbir.com", "wbko.com", "wbng.com",
    "wbrc.com", "wbtv.com", "wbtw.com", "wcjb.com", "wcpo.com",
    "wave3.com", "wavy.com", "walb.com", "wapt.com", "wate.com",
    "waff.com", "wafb.com", "wabi.tv", "waow.com", "wamu.org",
    "wane.com", "weau.com", "wbko.com", "wbaltv.com", "wcax.com",
    "wcyb.com", "weartv.com", "wevv.com", "wfft.com", "wflx.com",
    "wfxl.com", "wfxrtv.com", "wgal.com", "wgem.com", "wgme.com",
    "wgno.com", "wgxa.tv", "whec.com", "wmur.com", "wsbt.com",
    "wset.com", "wsil.com", "wsiltv.com", "wsls.com", "wspa.com",
    "wtap.com", "wtnh.com", "wtok.com", "wtol.com", "wtva.com",
    "wvah.com", "wvva.com", "wwlp.com", "wwnytv.com",
    "fox4kc.com", "fox5sandiego.com", "fox5vegas.com", "fox8.com",
    "fox8live.com", "fox10phoenix.com", "fox10tv.com", "fox11online.com",
    "fox13memphis.com", "fox16.com", "fox17.com", "fox17online.com",
    "fox19.com", "fox21news.com", "fox23.com", "fox23maine.com",
    "fox28media.com", "fox29.com", "fox35orlando.com", "fox38corpuschristi.com",
    "fox40.com", "fox40jackson.com", "fox42kptm.com", "fox43.com",
    "fox44news.com", "fox46.com", "fox47.com", "fox56.com", "fox59.com",
    "fox61.com", "foxbaltimore.com", "foxcarolina.com", "foxchattanooga.com",
    "foxillinois.com", "foxkansas.com", "foxlexington.com", "foxnebraska.com",
    "foxreno.com", "foxrichmond.com", "foxsanantonio.com",
    "nbcboston.com", "abc7ny.com",
    "spectrumnews1.com", "ny1.com", "spectrumlocalnews.com",
    "wach.com", "wchstv.com", "wcti12.com", "wcia.com",
    "pix11.com", "wphl17.com", "phl17.com", "mynbc15.com", "mynbc5.com",
    "myfox28columbus.com", "myfox8.com", "mytwintiers.com",
    "local12.com", "local21news.com", "localdvm.com", "localmemphis.com",
    "localwinnipeg.com", "localsyr.com", "localnews8.com",
    "koco.com", "kare11.com", "kadn.com", "kbsi23.com",
    "kdsm17.com", "kesq.com", "kfoxtv.com", "kfyl.com",
    "klax-tv.com", "kcra.com", "kcby.com", "kdrv.com",
    "khou.com", "khits.com", "kiem-tv.com", "kimatv.com",
    "klewtv.com", "kmph.com", "knopnews2.com", "koaa.com",
    "kpcw.com", "krdo.com", "kswo.com", "ktvb.com",
    "ktul.com", "ktvu.com", "kvia.com", "kvoa.com",
    "kxlf.com", "kyoutv.com", "kxtv.com", "keci.com",
    "12newsnow.com", "12news.com", "9news.com", "9news.com.au",
    "13abc.com", "13newsnow.com", "13wham.com", "7news.com.au",
    "10tv.com", "news3lv.com", "news4jax.com", "news4sanantonio.com",
    "news5cleveland.com", "news8000.com", "news9.com", "news10.com",
    "news24.com", "newschannel5.com", "newschannel6now.com",
    "newschannel9.com", "newschannel10.com", "newschannel20.com",
    "newsnationnow.com", "newsy.com",
    "clickorlando.com", "click2houston.com", "clickondetroit.com",
    "clickorlando.com", "cnycentral.com", "counton2.com", "cp24.com",
    "thedenverchannel.com", "wptv.com", "first-news.com",
    "firstcoastnews.com", "actionnews5.com", "actionnewsnow.com",
    "bakersfieldnow.com", "bigcountryhomepage.com",
    "borderreport.com", "brproud.com", "bringmethenews.com",
    "buffalonnews.com", "castanetsheridan.com", "cheddar.com",
    "cjonline.com", "cleveland.com", "cleveland19.com",
    "crossroadstoday.com", "dayton247now.com",
    "deltanews.tv", "dglobe.com", "duluthnewstribune.com",
    "eastidahonews.com", "fourstateshomepage.com",
    "grandforksherald.com", "hawkeyenow.com",
    "hawkeyenow.com", "hawaiinewsnow.com",
    "idahostatejournal.com", "insideevs.com",
    "kaaltv.com", "kait8.com", "kagstv.com",
    "kearneyhub.com", "kfvs12.com",
    "ktla.com", "ktvl.com", "kxii.com",
    "lacrossetribune.com", "laconiadailysun.com",
    "mahoning.com", "mlive.com",
    "nbc11news.com", "nbc16.com", "nbc24.com",
    "nbc25news.com", "nbc29.com",
    "necn.com", "noozhawk.com",
    "nwaonline.com", "nwitimes.com",
    "okcfox.com", "oanow.com",
    "pahomepage.com", "panolawatchman.com",
    "patch.com", "pennlive.com",
    "rapidcityjournal.com", "rocketcitynow.com",
    "siouxcityjournal.com", "siouxlandnews.com",
    "skyhinews.com", "sootoday.com",
    "sunherald.com", "sun-sentinel.com",
    "thenationaldesk.com", "tristatehomepage.com",
    "tulsa.com", "tulsaworld.com",
    "turnto10.com", "turnto23.com",
    "tv20detroit.com", "usnews.com",
    "valleynewslive.com", "valleycentral.com",
    "vcstar.com", "waow.com",
    "wane.com", "wapt.com",
    "wbaltv.com", "wbay.com",
    "wbko.com", "wbrc.com",
    "wcyb.com", "weau.com",
    "wenv.com", "weny.com",
    "westhawaiitoday.com", "westword.com",
    "wfft.com", "wfla.com",
    "wgal.com", "wgno.com",
    "whas11.com", "whnt.com",
    "wibw.com", "wifr.com",
    "wioa.com", "wishtv.com",
    "wistv.com", "witn.com",
    "wivb.com", "wjcl.com",
    "wjla.com", "wjtv.com",
    "wkbn.com", "wkbw.com",
    "wkow.com", "wkrn.com",
    "wlbt.com", "wlos.com",
    "wlwt.com", "wmar2news.com",
    "wmtw.com", "wnep.com",
    "wood.com", "woodtv.com",
    "wpde.com", "wpri.com",
    "wpta21.com", "wpxi.com",
    "wqow.com", "wral.com",
    "wrdw.com", "wreg.com",
    "wric.com", "wsav.com",
    "wsbtv.com", "wsfa.com",
    "wsmv.com", "wsoctv.com",
    "wspa.com", "wtae.com",
    "wthr.com", "wtmj.com",
    "wtnh.com", "wtok.com",
    "wtol.com", "wttg.com",
    "wtva.com", "wvpublic.org",
    "wvva.com", "wwltv.com",
    "wxow.com", "wymt.com",

    # ── Science / Health / Medicine / Research ───────────────────────────────
    "nature.com", "science.org", "sciencemag.org", "cell.com",
    "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov", "arxiv.org",
    "pnas.org", "bmj.com", "nejm.org", "thelancet.com", "jamanetwork.com",
    "cochranelibrary.com", "sciencedirect.com", "jstor.org", "ssrn.com",
    "who.int", "cdc.gov", "nih.gov", "fda.gov", "nasa.gov",
    "noaa.gov", "iaea.org", "wmo.int", "ipcc.ch",
    "hopkinsmedicine.org", "mayoclinic.org", "clevelandclinic.org",
    "webmd.com", "healthline.com", "medicalnewstoday.com", "medscape.com",
    "medpagetoday.com", "drugs.com", "verywellhealth.com",
    "scientificamerican.com", "newscientist.com", "sciencenews.org",
    "discovermagazine.com", "quantamagazine.org", "phys.org",
    "sciencedaily.com", "sciencealert.com", "medicalxpress.com",
    "eurekalert.org", "livescience.com", "plos.org",
    "healthdata.org", "healthaffairs.org", "statnews.com",
    "healio.com", "contagionlive.com", "cancer.org",
    "examine.com", "psychologytoday.com", "psychcentral.com", "psypost.org",
    "apa.org", "technologyreview.com", "techreview.com",
    "realclimate.org", "carbonbrief.org", "climatecentral.org",
    "earthsky.org", "cosmosmagazine.com", "futurism.com",
    "zmescience.com", "sciencing.com", "bigthink.com",
    "newatlas.com", "scitechdaily.com", "singularityhub.com",
    "aip.org", "agu.org", "aps.org", "ams.org", "acm.org", "ieee.org",
    "biospace.com", "biomedcentral.com",
    "nih.gov", "covid.gov", "coronavirus.gov",
    "iflscience.com", "sciencebasedmedicine.org", "healthfeedback.org",
    "climatefeedback.org", "climateactiontracker.org", "irena.org",
    "oceana.org", "paho.org", "unep.org", "ornl.gov",
    "socialmediatoday.com", "researchgate.net",
    "the-scientist.com", "americanscientist.org",

    # ── Fact-Checkers / Media Literacy ────────────────────────────────────────
    "snopes.com", "factcheck.org", "politifact.com", "fullfact.org",
    "boomlive.in", "altnews.in", "factly.in", "factchecker.in",
    "vishvasnews.com", "africacheck.org", "logically.ai", "leadstories.com",
    "checkyourfact.com", "verifythis.com", "truthorfiction.com",
    "aap.com.au", "dubawa.org", "maldita.es", "newtral.es", "correctiv.org",
    "dpa-factchecking.com", "mimikama.org", "pagellapolitica.it",
    "facta.news", "mymediachecker.com", "afpfactcheck.com",
    "stopfake.org", "bellingcat.com", "icij.org", "poynter.org",
    "adfontesmedia.com", "newsguardtech.com", "mediabiasfactcheck.com",
    "factcheck.afp.com", "newslaundry.com", "reporterslab.org",
    "americanpressinstitute.org", "niemanlab.org", "cjr.org",
    "rsf.org", "ifex.org", "ipi.media", "cpj.org",
    "fair.org", "procon.org", "logically.ai",

    # ── Government / Official Institutions ────────────────────────────────────
    "un.org", "europa.eu", "ec.europa.eu", "europarl.europa.eu",
    "gov.uk", "parliament.uk", "congress.gov", "whitehouse.gov",
    "state.gov", "defense.gov", "justice.gov", "fbi.gov",
    "ftc.gov", "sec.gov", "faa.gov", "epa.gov", "usda.gov",
    "gao.gov", "cbo.gov", "bls.gov", "census.gov", "bea.gov",
    "uscourts.gov", "supremecourt.gov", "usaspending.gov", "data.gov",
    "regulations.gov", "archives.gov", "loc.gov", "si.edu",
    "energy.gov", "usgs.gov", "nps.gov", "cfr.gov",
    "uscis.gov", "irs.gov", "dhs.gov",
    "india.gov.in", "pib.gov.in", "mea.gov.in", "mha.gov.in",
    "mohfw.gov.in", "pmo.gov.in", "rbi.org.in", "sebi.gov.in",
    "eci.gov.in", "uidai.gov.in", "gst.gov.in",
    "gov.au", "australia.gov.au", "rba.gov.au",
    "gov.ca", "canada.ca", "bankofcanada.ca",
    "gov.sg", "gov.jp", "gov.nz",
    "bankofengland.co.uk", "ecb.europa.eu", "bis.org",
    "imf.org", "worldbank.org", "oecd.org", "wto.org",
    "unicef.org", "undp.org", "unhcr.org", "wfp.org", "fao.org",
    "ilo.org", "icao.int", "imo.org", "itu.int",
    "osce.org", "nato.int", "coe.int",
    "interpol.int", "icrc.org", "msf.org",
    "icj-cij.org", "icc-cpi.int",
    "uscourts.gov", "scotusblog.com", "oyez.org", "law.com",

    # ── Academic / Think-Tanks / Policy ──────────────────────────────────────
    "harvard.edu", "mit.edu", "stanford.edu", "yale.edu",
    "princeton.edu", "columbia.edu", "cornell.edu", "upenn.edu",
    "uchicago.edu", "northwestern.edu", "duke.edu", "berkeley.edu",
    "ucla.edu", "ucsd.edu", "umich.edu", "cam.ac.uk", "ox.ac.uk",
    "imperial.ac.uk", "ucl.ac.uk", "lse.ac.uk", "ed.ac.uk",
    "manchester.ac.uk", "kcl.ac.uk", "ethz.ch", "epfl.ch",
    "caltech.edu", "iisc.ac.in", "iitb.ac.in", "iitd.ac.in",
    "nus.edu.sg", "ntu.edu.sg", "kyoto-u.ac.jp", "tokyo.ac.jp",
    "tifr.res.in", "britannica.com", "wikipedia.org", "wikimedia.org",
    "ourworldindata.org", "statista.com", "pewresearch.org", "gallup.com",
    "rand.org", "cfr.org", "brookings.edu", "csis.org",
    "piie.com", "epi.org", "cbpp.org", "taxfoundation.org",
    "taxpolicycenter.org", "cato.org", "hoover.org",
    "brenanncenter.org", "brennancenter.org", "aspeninstitute.org",
    "carnegieendowment.org", "cgdev.org", "atlanticcouncil.org",
    "nber.org", "iea.org", "krb.org",
    "hrw.org", "amnesty.org", "freedomhouse.org",
    "ire.org", "icij.org", "propublica.org",
    "lawfareblog.com", "justsecurity.org", "foreignaffairs.com",
    "foreignpolicy.com", "thediplomat.com", "fpri.org",
    "chathamhouse.org", "ecfr.eu", "crisisgroup.org",
    "weforum.org", "commonwealthfund.org", "kff.org", "khn.org",
    "healthdata.org", "guttmacher.org", "taxpayer.com",
    "americanactionforum.org", "bipartisanpolicy.org",
    "taxjustice.net", "itep.org", "crfb.org",
    "shortensteincenter.org", "knightfoundation.org",
    "constitution.org", "constitutioncenter.org",
    "democracynow.org", "theconversation.com", "aeon.co",
    "opendemocracy.net", "globalpolicy.org",
    "c4ads.org", "airwars.org", "38north.org",
    "isppi.org", "transpartisanreview.com",
    "insideedition.com", "insidehighered.com",
    "hechingerreport.org", "chalkbeat.org", "edweek.org",
    "universitybusiness.com", "chronicle.com",

    # ── Investigative / Long-form / Policy Journalism ────────────────────────
    "theintercept.com", "motherjones.com", "propublica.org",
    "thebureauinvestigates.com", "thecity.nyc", "thetrace.org",
    "revealnews.org", "publicintegrity.org", "icij.org",
    "dcist.com", "gothamist.com", "texastribune.org",
    "bridgemi.com", "vtdigger.org", "spotlightpa.org",
    "msmagazine.com", "colorlines.com", "19thnews.org",
    "undark.org", "thetyee.ca", "nationalobserver.com",
    "mississippitoday.org", "iowacapitaldispatch.com",
    "ohiocapitaljournal.com", "penncapital-star.com",
    "coloradosun.com", "nevadaindependent.com",
    "thenevadaindependent.com", "flatlandkc.org",
    "crosscut.com", "ctmirror.org", "newhampshirebulletin.com",
    "mainebeacon.com", "laist.com", "mountainstatespotlight.org",

    # ── Business / Finance / Economics ────────────────────────────────────────
    "bloomberg.com", "ft.com", "wsj.com", "economist.com", "barrons.com",
    "cnbc.com", "marketwatch.com", "fortune.com", "forbes.com",
    "businessinsider.com", "inc.com", "fastcompany.com", "entrepreneur.com",
    "hbr.org", "americanbanker.com", "investopedia.com",
    "morningbrew.com", "axios.com", "qz.com", "thestreet.com",
    "prnewswire.com", "businesswire.com",

    # ── Technology ────────────────────────────────────────────────────────────
    "wired.com", "techcrunch.com", "theverge.com", "arstechnica.com",
    "engadget.com", "cnet.com", "zdnet.com", "anandtech.com",
    "thenextweb.com", "venturebeat.com", "protocol.com",
    "technologyreview.com", "spectrum.ieee.org", "techspot.com",
    "bleepingcomputer.com", "bgr.com", "howtogeek.com", "lifehacker.com",
    "gizmodo.com", "kotaku.com",

    # ── Sports ────────────────────────────────────────────────────────────────
    "espn.com", "espncricinfo.com", "skysports.com", "cricbuzz.com",
    "bleacherreport.com",

    # ── General Verified Sources ──────────────────────────────────────────────
    "vox.com", "slate.com", "theweek.com", "newyorker.com",
    "newrepublic.com", "newstatesman.com", "spectator.co.uk",
    "thehill.com", "politico.com", "rollcall.com", "morningconsult.com",
    "fivethirtyeight.com", "opensecrets.org", "followthemoney.org",
    "ballotpedia.org", "votesmart.org", "c-span.org", "cookpolitical.com",
    "rasmussenreports.com", "ipsos.com", "angusreid.org",
    "rappler.com", "globalcitizen.org", "nber.org",
    "worldometers.info", "usafacts.org", "ourworldindata.org",
    "ground.news", "mediapost.com", "adweek.com",
    "religionnews.com", "christianitytoday.com", "cruxnow.com",
    "americamagazine.org", "commonwealmagazine.org",
    "environmentaldefense.org", "earthjustice.org", "nrdc.org",
    "cleantechnica.com", "insideclimatenews.org", "grist.org",
    "carbonbrief.org", "climatechangenews.com", "ecowatch.com",
    "mongabay.com", "anthropocenemagazine.org",
    "military.com", "militarytimes.com", "airforcetimes.com",
    "armytimes.com", "navytimes.com", "defensenews.com",
    "defenseone.com", "breakingdefense.com", "stripes.com",
    "lawandcrime.com", "law360.com", "scotusblog.com",
    "nationalgeographic.com", "smithsonianmag.com",
    "history.com", "biographyfacts.com", "biography.com",
    "biography.com", "britannica.com", "thoughtco.com",
    "atlasobscura.com",
}



class WebCorroborator:
    """
    Searches the web via Tavily for articles similar to the input,
    filters results by trusted domains, and returns a corroboration score.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.tavily_api_key
        if not key:
            raise ValueError("Tavily API key not set. Add TAVILY_API_KEY to .env")
        self.client = TavilyClient(api_key=key)

    # ── Public API ────────────────────────────────────────────────────────────

    def corroborate(self, title: str, text: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for news articles covering the same event/topic.

        Returns a dict with:
          - corroboration_score (0.0–1.0)
          - trusted_sources_found (int)
          - total_results_found (int)
          - matched_sources (list of dicts with url, title, snippet, domain, trusted)
          - search_query (str)
        """
        query = self._build_query(title, text)
        raw_results = self._tavily_search(query, max_results)

        if not raw_results:
            return self._empty_result(query)

        matched = self._classify_results(raw_results)
        trusted_count = sum(1 for r in matched if r["trusted"])
        score = self._compute_score(trusted_count, len(matched))

        return {
            "corroboration_score": score,
            "trusted_sources_found": trusted_count,
            "total_results_found": len(matched),
            "matched_sources": matched,
            "search_query": query,
        }

    def scrape_article_text(self, url: str) -> Optional[str]:
        """Use trafilatura to scrape clean article text from a URL."""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        return None

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _build_query(self, title: str, text: str) -> str:
        """Build a focused search query from the article title + key noun phrases."""
        # Use the title as the primary query; append first 80 chars of text for context
        title_clean = title.strip().strip('"').strip("'")
        context = text[:80].strip().replace("\n", " ")
        return f"{title_clean} {context}"[:200]

    def _tavily_search(self, query: str, max_results: int) -> List[Dict]:
        """Call Tavily news search and return raw results."""
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                topic="news",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
            )
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []

    def _classify_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Tag each result as trusted or not and normalize fields."""
        classified = []
        for r in results:
            url = r.get("url", "")
            domain = self._extract_domain(url)
            trusted = any(td in domain for td in TRUSTED_DOMAINS)
            classified.append({
                "url": url,
                "title": r.get("title", ""),
                "snippet": r.get("content", "")[:300],
                "domain": domain,
                "trusted": trusted,
                "score": r.get("score", 0.0),
            })
        return classified

    def _compute_score(self, trusted_count: int, total: int) -> float:
        """
        Score logic:
        - 3+ trusted sources → 0.90
        - 2 trusted sources  → 0.75
        - 1 trusted source   → 0.55
        - 0 trusted sources  → proportional penalty based on total results
        """
        if trusted_count >= 3:
            return round(min(0.70 + (trusted_count * 0.05), 1.0), 3)
        elif trusted_count == 2:
            return 0.75
        elif trusted_count == 1:
            return 0.55
        else:
            # No trusted sources — penalise based on how many untrusted ones exist
            if total == 0:
                return 0.15   # Story found nowhere — very suspicious
            elif total <= 2:
                return 0.25   # Story barely found
            else:
                return 0.35   # Found on many sites, but none trusted

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.lower().replace("www.", "")
        except Exception:
            return url

    def _empty_result(self, query: str) -> Dict[str, Any]:
        return {
            "corroboration_score": 0.15,
            "trusted_sources_found": 0,
            "total_results_found": 0,
            "matched_sources": [],
            "search_query": query,
        }
