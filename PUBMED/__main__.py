import requests
from bs4 import BeautifulSoup
import csv
import re
import argparse
from typing import List,Dict,Optional
ESEARCH_URL="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
#search pub med and getting paper ids
def search_pubmed(query:str)->List[str]:
    """
    This Function sends Query to the PubMed esearch API and retrives matching PubMed IDs.
    Args:
      query(str):The search keyword or phrase.
    Returns:
      List[str]:A list of matching PubMed IDs.
    """
    if not query.strip():
        print("❌ Empty query provided")
        return []
    params={
        "db":"pubmed",
        "term":query,
        "retmax":5,
        "retmode":"xml"
    }
    try:
        response=requests.get(ESEARCH_URL,params=params,timeout=10)
        response.raise_for_status()
        soup=BeautifulSoup(response.text,"xml")#using beautiful soup to get text and convert to xml
        ids:List[str]=[tag.text for tag in soup.find_all("Id")]
        return ids
    except requests.RequestException as e:
        print(f"❌ Failed to fetch search results:{e}")
    except Exception  as e:
        print(f"❌ Error parsing search response:{e}")
#fetching the information
def fetch_paper_details(paper_ids:List[str],debug=False)->List[Dict[str,str]]:
    """
    This Function Fetches metadata for a list of PubMed IDs and extracts non-academic author info.
    Args:
        paper_ids (List[str]): List of PubMed article IDs.
        debug (bool): Whether to print debug output.

    Returns:
        List[Dict[str, str]]: A list of dictionaries with extracted fields.
    """
    params={
        "db":"pubmed",
        "id":",".join(paper_ids),
        "retmode":"xml"
    }
    response=requests.get(EFETCH_URL,params=params,timeout=15)
    response.raise_for_status()
    soup=BeautifulSoup(response.text,"xml")
    articles=soup.find_all("PubmedArticle")
    results:List[Dict[str,str]]=[]
    for article in articles:
        try:
            title_tag=article.find("ArticleTitle")
            title:str=title_tag.text.strip() if title_tag else "No title"
            pmid:str=article.find("PMID").text.strip()
            #Logic to find publication date
            pub_date=article.find("PubDate")
            if pub_date:
                year=pub_date.find("Year")
                month=pub_date.find("Month")
                day=pub_date.find("Day")
                publication_date:str=""
                if year:
                    publication_date+=year.text
                if month:
                    publication_date+=f"-{month.text}"
                if day:
                    publication_date+=f"-{day.text}"
            else:
                publication_date:str="Unknown"
            #extracting corresponding email
            corresponding_email:str="Not found"
            for tag in article.find_all("Affiliation"):
                if tag:
                    aff_text:str=tag.text.strip()
                    if debug:
                        print("📄 checking affiliation:",aff_text)
                    email:str=extract_email(aff_text)
                    if debug:
                        print("📧 Extracted email:",email)
                    if email!="Not found":
                        corresponding_email=email
                        break
                    
            #Logic to find author name
            for author in article.find_all("Author"):
                first=author.find("Forename")
                last=author.find("LastName")
                name:str="Unknown"
                if first and last:
                    name=f"{first.text}{last.text}"
                elif last:
                    name=last.text
                elif author.find("CollectiveName").text:
                    name=author.find("CollectiveName").text
                #logic to check whether affiliation is academic or not
                aff_info=author.find("AffiliationInfo")
                if aff_info:
                    aff_tag=aff_info.find("Affiliation")
                    if aff_tag:
                        affiliation:str=aff_tag.text
                    if is_non_academic(affiliation):
                        results.append({
                            "PubmedID":pmid,
                            "Title":title,
                            "Publication Date":publication_date,
                            "Non-academic Author(s)":name,
                            "Company Affiliation(s)":affiliation,
                            "Corresponding Author Email":corresponding_email
                        })
        except Exception as e:
            print("❌Error reading article:",e)
    return results

#checking the academic
def is_non_academic(affiliation:str)->bool:
    """
    Determines whether an affiliation is non-academic.
    Args:
        affiliation (str): The full affiliation string.
    Returns:
        bool: True if non-academic, False if academic.
    """
    if not affiliation:
        return False
    affil=affiliation.lower()
    academic_keywords=[
        "university","college","institute","school","hospital","center","centre"
    ]
    return not any(word in affil for word in academic_keywords)
#email extraction function
def extract_email(text:str)->str:
    """
    Extracts the first email address from a given text string.
    Args:
        text (str): Input text (typically affiliation).
    Returns:
        str: The extracted email address or 'Not found' if none is present.
    """
    #strip whitespace and surrounding punctuations
    text=text.strip().replace("\n"," ")
    matches=re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",text)
    if matches:
        return matches[0].strip().strip(".;,")
    return "Not Found"
#csv file conversion
def save_to_csv(data:List[Dict[str,str]],filename:str)->None:
    """
    Saves a list of dictionaries to a CSV file.
    Args:
        data (List[Dict[str, str]]): The data to write.
        filename (str): Name of the CSV file.
    """
    if not data:
        print("⚠️ No Data To Save")
        return
    with open(filename,"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["PubmedID","Title","Publication Date","Non-academic Author(s)","Company Affiliation(s)","Corresponding Author Email"])
        writer.writeheader()
        writer.writerows(data)
    print(f"✅Saved {len(data)} results to {filename}")
    

def main()->None:
    """
    CLI entry point. Parses arguments and runs the program.
    """
    parser=argparse.ArgumentParser(description="Fetch PubMed papers and filter non-academic authors from PubMed")
    parser.add_argument("--query",type=str,required=True,help="PubMed search term(example:'diabetes treatment')")
    parser.add_argument("--file",type=str,default="output.csv",help="Specify the filename to save the results.(Default:output.csv)")
    parser.add_argument("--debug",action="store_true",help="Prints debug information during execution.")
    
    args=parser.parse_args()
    #enable debug mode
    if args.debug:
        print(f"🔍 Searching PubMed for : {args.query}")
    ids=search_pubmed(args.query)
    if not ids:
        print(f"❌ No results found.")
    else:
        if args.debug:
            print(f"✅ Found {len(ids)} papers. Fetching Details .....")
        data=fetch_paper_details(ids,debug=args.debug)
        save_to_csv(data,args.file)

if __name__=="__main__":
    main()

