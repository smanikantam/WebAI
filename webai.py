import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
user_data={
    1:"Manikantam",                 #first name
    2:"Sadam",                      #last name
    3:"sadammanikantam@gmail.com",  #email
    4:"9866445361",                 #Number
    5:"20-09-2002",                 #birthday
    6:"Male",                       #gender
}
class WebSite:
    def __init__(self, text,  link, depth):
        self.text=text
        self.name = urlparse(link).netloc
        self.link = link
        self.internal = {}
        self.external = []
        self.other = []
        self.depth =depth

    def create_website_tree(self, root, unique_links, max_depth, base_domain):
        if root.depth >= max_depth:
            return

        response = requests.get(root.link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # All Website links
        for link in soup.find_all('a'):
            try:
                href = urlparse(link['href'])
                if href in unique_links:
                    continue
                elif(href.scheme not in ["https","http",""]):
                    continue
                
                #If the href is fragement then it falls under catogery of internal
                elif (href.scheme=="" and href.netloc=="") and (href.fragment!="" and href.path==""):
                    internal_link = root.name + link["href"]
                    root.internal[link.text] = internal_link
                    unique_links.add(internal_link)

                #If the href is a link of same domain but another page then it falls under external
                elif (href.netloc==base_domain or href.netloc=="") and (href.path!=""):
                    if(href.netloc==""):
                        temp = WebSite(link.text,"https://"+root.name+"/"+link["href"], root.depth + 1)
                    else:
                        temp = WebSite(link.text,"https://"+link["href"], root.depth + 1)
                    root.external.append(temp)
                    unique_links.add(link["href"])

                #if the href is other domain then it falls under other catogery
                elif (href.scheme!="" and href.netloc!=base_domain):
                    temp=WebSite(link.text,link["href"],root.depth+1)
                    root.other.append(temp)
                    unique_links.add(link["href"])
                
                
            except:
                print("entered except")

        for external_link in root.external:
            external_link.create_website_tree(external_link, unique_links, max_depth, base_domain)
        for other_link in root.other:
            other_link.create_website_tree(other_link,unique_links,max_depth,base_domain)

    def display_tree(self,root,unique_links):
        unique_links.add(root.link)
        if(len(root.internal)==0 and len(root.external)==0 and len(root.other)==0):
            return

        # Display INTERNAL redirects links
        for name, link in root.internal.items():
            if(link in unique_links):
                continue
            print(f"INTERNAL LINK : {name} -> {link} , {root.depth}")

        # Display EXTERNAL redirects links
        for external_link in root.external:
            if(external_link.link in unique_links):
                continue
            print(f"EXTERNAL LINK : {external_link.text} -> {external_link.link} , {external_link.depth}")
            self.display_tree(external_link,unique_links)

        # Display OTHER redirects links
        for other_link in root.other:
            if(other_link.link in unique_links):
                continue
            print(f"OTHER LINK : {other_link.text} -> {other_link.link} , {other_link.depth}")
            self.display_tree(other_link,unique_links)

    def search_signup_form(self, root):
        # print(f"Name: {root.name}, Link: {root.link}, Depth: {root.depth}")

        # search INTERNAL redirects links
        for name, link in root.internal.items():  # .items() return the pair in the dict that is key and value
            if(name == "Sign Up"):
                return link

        # search EXTERNAL redirects links
        for external_link in root.external:
            if(external_link.text=="Sign Up"):
                return external_link.link
            self.search_signup_form(external_link)

        # # search OTHER redirects links
        # for other_link in root.other:
        #     self.search_signup_form(other_link)

    def fill_signup_form(self,link):
        try:
            # Send a GET request to the website's link
            response = requests.get(link)
            print(link)
            if response.status_code != 200:
                print(f"Failed to access the website: {response.status_code}")
                return

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Locate the sign-up form (You'll need to customize this part)
            # For example, you can find it based on certain attributes like class or ID
            signup_form = soup.find('form')

            if signup_form:
                # Extract the form fields (input names or IDs)
                form_fields = signup_form.find_all('input')

                # Prepare form data with sample values (customize as needed)
                form_data = {}
                for field in form_fields:
                    if(field.get("type")!="hidden" and field.get("aria-required")):
                        print(field.get('name'),field.get("aria-label"))
                        form_data[field.get('name')] = 'sample_value'

                # Perform actions on the form, such as filling in fields and submitting
                # You can use a library like Selenium for more complex interactions.

                # Example: Sending a POST request with form data
                response = requests.post(signup_form['action'], data=form_data)

                # Check the response for success or errors
                if response.status_code == 200:
                    print("Sign-up successful!")
                else:
                    print("Sign-up failed. Check for errors in the response.")

            else:
                print("Sign-up form not found on the page.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    


if(__name__=="__main__"):
    root = WebSite("facebook","https://forfof.me",depth=0)
    unique_links = set()
    max_depth = 2  # Set your desired depth limit here

    root.create_website_tree(root, unique_links, max_depth, root.name)
    
    # Call the function to display the entire tree
    unique_links = set()
    root.display_tree(root,unique_links)


    form_link=root.search_signup_form(root)
    if(form_link!=None):
        print("Hey there is a form",end=" : \n")
        root.fill_signup_form(form_link)


