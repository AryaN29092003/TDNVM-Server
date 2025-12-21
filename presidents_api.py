from fastapi import FastAPI, HTTPException,Body
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError
from datetime import date,datetime
from typing import Union,List,Optional
from pydantic import BaseModel
from googletrans import Translator
import json
import os
from deep_translator import GoogleTranslator

Translator= Translator()


class user(BaseModel):
    first_name: str
    last_name: str
    phone: str
    city: str
    state: str

    class Config:
        allow_population_by_field_name = True
        fields = {
            "first_name": "firstName",
            "last_name": "lastName",
        }

class UserUpdateRequest(BaseModel):
    phone: str
    status: str

class EventDeleteRequest(BaseModel):
    id: int

class DeleteRequest(BaseModel):
    srno: int

class Event(BaseModel):
    title: str
    description: str
    date: date
    location: str
    year: int
    category: str
    images: List[str]   # multiple images

class GalleryEvent(BaseModel):
    title: str
    description: str
    date: date
    location: str
    year: int
    category: str
    folder_url: str

class UpdateEvent(BaseModel):
    id: int
    title: str
    description: str
    date: date
    location: str
    year: int
    category: str
    images: Union[List[str], str]   # multiple images

class UpdateGalleryEvent(BaseModel):
    id: int
    title: str
    description: str
    date: date
    location: str
    year: int
    category: str
    folder_url: Optional[str] = None

class MemberDetail(BaseModel):
    fullname:str
    address:str
    birthdate:datetime

class UpdateMember(BaseModel):
    id: int
    fullname: str
    address: str
    birthdate: datetime 

class CoreTeamMember(BaseModel):
    name:str
    designation:str
    photo:str
    description:str
    email:str
    phone:str
    linkedin:str
    experience:str
    achievements:str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:5174","http://127.0.0.1:5173","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="tdnvm"
    )

@app.get("/")
def index():
    return {"message": "Hello, World!"}

@app.get("/presidents", response_model=List[Dict])
def get_all_members():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM presidents_secretaries;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/core_team_en", response_model=List[Dict])
def get_all_members():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM core_team_en;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.post("/add_coreteam_en")
def create_event(member: CoreTeamMember):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        

        query = """
        INSERT INTO core_team_en (name,designation, photo, description,email,phone,linkedin,experience,achievements)
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s);
        """
        values = (
            member.name,
            member.designation,
            member.photo,
            member.description,
            member.email,
            member.phone,
            member.linkedin,
            member.experience,
            member.achievements
            
        )

        cursor.execute(query, values)
        connection.commit()

        new_id = cursor.lastrowid 

        new_member={
            'id':new_id,
            'name': member.name,
            'designation': member.designation,
            'photo': member.photo,
            'description': member.description,
            'email': member.email,
            'phone': member.phone,
            'linkedin': member.linkedin,
            'experience': member.experience,
            'achievements': member.achievements,
            }
        
        new_member_gu={
            'id':new_id,
            'name': GoogleTranslator(source='auto', target='gu').translate(member.name),
            'designation': GoogleTranslator(source='auto', target='gu').translate(member.designation),
            'photo': member.photo,
            'description': GoogleTranslator(source='auto', target='gu').translate(member.description),
            'email': member.email,
            'phone': member.phone,
            'linkedin': member.linkedin,
            'experience': member.experience,
            'achievements': GoogleTranslator(source='auto', target='gu').translate(member.achievements),
        }

        query = """
        INSERT INTO core_team_gu 
        (id, name, designation, photo, description, email, phone, linkedin, experience, achievements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            new_member_gu['id'],
            new_member_gu['name'],
            new_member_gu['designation'],
            new_member_gu['photo'],
            new_member_gu['description'],
            new_member_gu['email'],
            new_member_gu['phone'],
            new_member_gu['linkedin'],
            new_member_gu['experience'],
            new_member_gu['achievements']
        )

        cursor.execute(query, values)
        connection.commit()

        print(new_member_gu)
        return {"message": "core team member added successfully", "member": new_member}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.put("/update_coreteam_en")
def update_coreteam_member(member: CoreTeamMember):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        member_id = member.id  # ✅ Ensure CoreTeamMember model has an `id` field

        # 1. Check if member exists
        cursor.execute("SELECT * FROM core_team_en WHERE id = %s", (member_id,))
        existing = cursor.fetchone()
        if not existing:
            connection.close()
            raise HTTPException(status_code=404, detail="Member not found")

        # 2. Update member
        cursor.execute(
            """
            UPDATE core_team_en
            SET name=%s, designation=%s, photo=%s, description=%s,
                email=%s, phone=%s, linkedin=%s, experience=%s, achievements=%s
            WHERE id=%s
            """,
            (
                member.name,
                member.designation,
                member.photo,
                member.description,
                member.email,
                member.phone,
                member.linkedin,
                member.experience,
                member.achievements,
                member_id,
            ),
        )
        connection.commit()

        # 1. Check if member exists
        cursor.execute("SELECT * FROM core_team_gu WHERE id = %s", (member_id,))
        existing = cursor.fetchone()
        if not existing:
            connection.close()
            raise HTTPException(status_code=404, detail="Member not found")

        # 2. Update member
        cursor.execute(
            """
            UPDATE core_team_gu
            SET name=%s, designation=%s, photo=%s, description=%s,
                email=%s, phone=%s, linkedin=%s, experience=%s, achievements=%s
            WHERE id=%s
            """,
            (
                GoogleTranslator(source='auto', target='gu').translate(member.name),
                GoogleTranslator(source='auto', target='gu').translate(member.designation),
                member.photo,
                GoogleTranslator(source='auto', target='gu').translate(member.description),
                member.email,
                member.phone,
                member.linkedin,
                member.experience,
                GoogleTranslator(source='auto', target='gu').translate(member.achievements),
                member_id,
            ),
        )
        connection.commit()

        connection.close()

        return {"message": f"Member {member_id} updated successfully"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))



class DeleteMember(BaseModel):
    id: int

@app.delete("/delete_coreteam_en")
def delete_coreteam_member(member: DeleteMember):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        member_id = member.id

        # 1. Check if member exists
        cursor.execute("SELECT * FROM core_team_en WHERE id = %s", (member_id,))
        existing = cursor.fetchone()
        if not existing:
            connection.close()
            raise HTTPException(status_code=404, detail="Member not found")

        # 2. Delete member
        cursor.execute("DELETE FROM core_team_en WHERE id=%s", (member_id,))
        connection.commit()
        # connection.close()

         # 1. Check if member exists
        cursor.execute("SELECT * FROM core_team_gu WHERE id = %s", (member_id,))
        existing = cursor.fetchone()
        if not existing:
            connection.close()
            raise HTTPException(status_code=404, detail="Member not found")

        # 2. Delete member
        cursor.execute("DELETE FROM core_team_gu WHERE id=%s", (member_id,))
        connection.commit()
        connection.close()

        return {"message": f"Member {member_id} deleted successfully"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/core_team_gu", response_model=List[Dict])
def get_all_members():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM core_team_gu;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def normalize_images(images_value: str | None):
    if not images_value:
        return []

    images_value = images_value.strip()

    # Multiple images (pipe-separated)
    if "|" in images_value:
        return [img.strip() for img in images_value.split("|") if img.strip()]

    # Single image URL (may contain commas)
    return [images_value]

@app.get("/events_gu", response_model=List[Dict])
def get_all_events_gu():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM events_gu;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Fix images column if it's a JSON string
            if "images" in row_dict and row_dict["images"]:
                try:
                    row_dict["images"] = normalize_images(row_dict.get("images"))
                except Exception:
                    row_dict["images"] = []
            
            members.append(row_dict)

        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/events_en", response_model=List[Dict])
def get_all_events_en():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM events_en;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        # members = [dict(zip(columns, row)) for row in rows]

        members = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Fix images column if it's a JSON string
            if "images" in row_dict and row_dict["images"]:
                try:
                    row_dict["images"] = normalize_images(row_dict.get("images"))
                except Exception:
                    row_dict["images"] = []
            
            members.append(row_dict)
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/add_events_en")
def create_event(event: Event):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        folder_url = event.images[0]
        # Convert list of images into comma-separated string (or use JSON if column supports it)
        print(folder_url)
        try:
            # Allowed image extensions
            allowed_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            image_files =[]
            # --- STEP 1: Check if folder_url itself is an image file ---
            if folder_url.lower().endswith(allowed_extensions):
                # Direct image URL or file path → treat as a single image
                # images_str = folder_url
                image_files.append(folder_url)
            else:
                # --- STEP 2: Otherwise treat it as a directory ---
                if not os.path.isdir(folder_url):
                    raise FileNotFoundError(f"Folder not found: {folder_url}")

                # Filter files by extension
                image_files = [
                    f for f in os.listdir(folder_url)
                    if os.path.isfile(os.path.join(folder_url, f)) and f.lower().endswith(allowed_extensions)
                ]

                # Convert file names to full paths
                image_files = [os.path.join(folder_url, f) for f in image_files]

                images_str = ",".join(image_files)
            

        except Exception as e:
            print(f"Error: {e}")
            # return []
        images_str = ",".join(image_files)
        

        query = """
        INSERT INTO events_en (title, description, date, location, year, category, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            event.title,
            event.description,
            event.date,
            event.location,
            event.year,
            event.category,
            images_str
        )

        cursor.execute(query, values)
        connection.commit()

        
        new_id = cursor.lastrowid  

        new_event={
            'id':new_id,
            'title': event.title,
            'description':event.description,
            'date':event.date,
            'location': event.location,
            'year': event.year,
            'category': event.category,
            'images':event.images,}
            
        new_event_gu={
            'id':new_id,
            'title':GoogleTranslator(source='auto', target='gu').translate(event.title),
            'description': GoogleTranslator(source='auto', target='gu').translate(event.description),
            'date':event.date,
            'location':  GoogleTranslator(source='auto', target='gu').translate(event.location),
            'year': event.year,
            'category':GoogleTranslator(source='auto', target='gu').translate(event.category),
            'images':event.images,}
            
        query_gu = """
        INSERT INTO events_gu (id, title, description, date, location, year, category, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        values_gu = (
            new_event_gu['id'],
            new_event_gu['title'],
            new_event_gu['description'],
            new_event_gu['date'],
            new_event_gu['location'],
            new_event_gu['year'],
            new_event_gu['category'],
            images_str  
        )

        cursor.execute(query_gu, values_gu)
        connection.commit()

            # 'name': Translator.translate(member.name,dest='gu').text,


        # # fetch inserted row
        # cursor.execute("SELECT * FROM events_en WHERE id = %s", (new_id,))
        # new_event = cursor.fetchone()

        return {"message": "Event created successfully", "event": new_event}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.put("/update_event_en")
def update_member(event: UpdateEvent):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    id= event.id
    if event.images is not None:
        images = event.images

    cursor.execute("SELECT * FROM events_en WHERE id = %s", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")

    # -------------------------------
    # PROCESS IMAGES PROPERLY
    # -------------------------------
    images_str = existing["images"] 
    print(images)
    if isinstance(images, list) and len(images) > 0:
        folder_url = event.images[0]
        print(folder_url)
        # Convert list of images into comma-separated string (or use JSON if column supports it)
        try:
            allowed_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            image_files =[]
            # --- STEP 1: Check if folder_url itself is an image file ---
            if folder_url.lower().endswith(allowed_extensions):
                # Direct image URL or file path → treat as a single image
                # images_str = folder_url
                image_files.append(folder_url)
            else:
                # --- STEP 2: Otherwise treat it as a directory ---
                if not os.path.isdir(folder_url):
                    raise FileNotFoundError(f"Folder not found: {folder_url}")

                # Filter files by extension
                image_files = [
                    f for f in os.listdir(folder_url)
                    if os.path.isfile(os.path.join(folder_url, f)) and f.lower().endswith(allowed_extensions)
                ]

                # Convert file names to full paths
                image_files = [os.path.join(folder_url, f) for f in image_files]

                images_str = ",".join(image_files)

        except Exception as e:
            print(f"Error: {e}")
            # return []
        images_str = ",".join(image_files)
    # -------------------------
    # CASE 2: single URL sent as string
    # -------------------------
    elif isinstance(images, str) and images.strip():

        allowed_extensions = ('.jpg', '.jpeg', '.png', '.webp')

        # If it's a single image URL
        if images.lower().endswith(allowed_extensions):
            images_str = images  # use the new one
        else:
            # If not an image → ignore and keep existing
            images_str = existing["images"]

    # -------------------------
    # CASE 3: images is None or empty → keep existing
    # -------------------------
    else:
        images_str = existing["images"]
        print(images_str)
    # 1. Check if event exists
    cursor.execute("SELECT * FROM events_en WHERE id = %s", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Update event
    cursor.execute(
        """
        UPDATE events_en
        SET title = %s, description = %s, date = %s, location = %s, year = %s, category = %s, images = %s
        WHERE id = %s
        """,
        (event.title, event.description, event.date, event.location, event.year, event.category, images_str, id),
    )
    conn.commit()

    # 1. Check if event exists
    cursor.execute("SELECT * FROM events_gu WHERE id = %s", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")

    cursor.execute(
        """
        UPDATE events_gu
        SET title = %s, description = %s, date = %s, location = %s, year = %s, category = %s, images = %s
        WHERE id = %s
        """,
        (GoogleTranslator(source='auto', target='gu').translate(event.title), GoogleTranslator(source='auto', target='gu').translate(event.description), event.date, GoogleTranslator(source='auto', target='gu').translate(event.location), event.year, GoogleTranslator(source='auto', target='gu').translate(event.category), images_str, id),
    )
    conn.commit()

    cursor.execute("SELECT * FROM events_en WHERE id = %s", (id,))
    updated_event = cursor.fetchone()

    conn.close()

    return updated_event

@app.delete("/delete_event_en")
def delete_member(request: EventDeleteRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    id= request.id

    cursor.execute("SELECT * FROM events_en WHERE id = %s", (id,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    cursor.execute("DELETE FROM events_en WHERE id = %s", (id,))
    conn.commit()

    cursor.execute("SELECT * FROM events_gu WHERE id = %s", (id,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")
    cursor.execute("DELETE FROM events_gu WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return {"message": f"Member {id} deleted successfully"}


@app.get("/gallery_events_en", response_model=List[Dict])
def get_all_gallery_events_en():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM gallery_events_en;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Fix images column if it's a JSON string
            if "images" in row_dict and row_dict["images"]:
                try:
                    row_dict["images"] = normalize_images(row_dict.get("images"))
                except Exception:
                    row_dict["images"] = []
            
            members.append(row_dict)
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.post("/gallery_events_en")
def create_gallery_event(event: GalleryEvent):
    folder_url_list= event.folder_url.split("\\")
    folder_url = "/".join(folder_url_list)
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Convert list of images into comma-separated string (or use JSON if column supports it)
        try:
            if not os.path.isdir(folder_url):
                raise FileNotFoundError(f"Folder not found: {folder_url}")

            # Allowed extensions
            allowed_extensions = ('.jpg', '.jpeg', '.webp')

            # Filter files by extension
            image_files = [
                f for f in os.listdir(folder_url)
                if os.path.isfile(os.path.join(folder_url, f)) and f.lower().endswith(allowed_extensions)
            ]
            # return image_files
            for i in range(len(image_files)):
                image_files[i] = folder_url + "/" + image_files[i]

        except Exception as e:
            print(f"Error: {e}")
            # return []
        images_str = ",".join(image_files)
        # print=images_str
        query = """
        INSERT INTO gallery_events_en (title, description, date, location, year, category, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            event.title,
            event.description,
            event.date,
            event.location,
            event.year,
            event.category,
            images_str
        )


        cursor.execute(query, values)
        

        connection.commit()

        new_id = cursor.lastrowid  

        new_event={
            'id':new_id,
            'title': event.title,
            'description':event.description,
            'date':event.date,
            'location': event.location,
            'year': event.year,
            'category': event.category,
            'images':images_str,}
        
        
        query = """
        INSERT INTO gallery_events_gu (id,title, description, date, location, year, category, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        # translator = Translator()
        gu_title = GoogleTranslator(source='auto', target='gu').translate(event.title)
        gu_description = GoogleTranslator(source='auto', target='gu').translate(event.description)
        gu_location = GoogleTranslator(source='auto', target='gu').translate(event.location)
        gu_category = GoogleTranslator(source='auto', target='gu').translate(event.category)

        values = (
            new_id,
            gu_title,
            gu_description,
            event.date,
            gu_location,
            event.year,
            gu_category,
            images_str
        )

        # print(values)
        cursor.execute(query, values)

        connection.commit()

        return {"message": "Event created successfully", "event": new_event}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/update_gallery_event_en")
def update_member(event: UpdateGalleryEvent):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    id= event.id
    print(event)
    folder_url = event.folder_url
    # 1. Check if event exists
    cursor.execute("SELECT * FROM gallery_events_en WHERE id = %s", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")
    
    if isinstance(folder_url, str):
        # Convert list of images into comma-separated string (or use JSON if column supports it)
        try:
            folder_url_list=folder_url.split("\\")
            folder_url = "/".join(folder_url_list)
            if not os.path.isdir(folder_url):
                raise FileNotFoundError(f"Folder not found: {folder_url}")

            # Allowed extensions
            allowed_extensions = ('.jpg', '.jpeg', '.webp')

            # Filter files by extension
            image_files = [
                f for f in os.listdir(folder_url)
                if os.path.isfile(os.path.join(folder_url, f)) and f.lower().endswith(allowed_extensions)
            ]
            # return image_files
            for i in range(len(image_files)):
                image_files[i] = folder_url + "/" + image_files[i]

        except Exception as e:
            print(f"Error: {e}")
            # return []
        images_str = ",".join(image_files)
    else:
        images_str = existing['images']
    

    # 2. Update event
    cursor.execute(
        """
        UPDATE gallery_events_en
        SET title = %s, description = %s, date = %s, location = %s, year = %s, category = %s, images = %s
        WHERE id = %s
        """,
        (event.title, event.description, event.date, event.location, event.year, event.category, images_str, id),
    )
    conn.commit()

    # 1. Check if event exists
    cursor.execute("SELECT * FROM gallery_events_gu WHERE id = %s", (id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")
    
    cursor.execute(
        """
        UPDATE gallery_events_gu
        SET title = %s, description = %s, date = %s, location = %s, year = %s, category = %s, images = %s
        WHERE id = %s
        """,
        (
            GoogleTranslator(source='auto', target='gu').translate(event.title),
            GoogleTranslator(source='auto', target='gu').translate(event.description),
            event.date,
            GoogleTranslator(source='auto', target='gu').translate(event.location),
            event.year,
            GoogleTranslator(source='auto', target='gu').translate(event.category),
            images_str,
            id),
    )    
    conn.commit()
    conn.close()

    return {"message": f"Member {id} updated successfully"}

@app.delete("/delete_gallery_event_en")
def delete_member(request: EventDeleteRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    id= request.id

    cursor.execute("SELECT * FROM gallery_events_en WHERE id = %s", (id,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    cursor.execute("DELETE FROM gallery_events_en WHERE id = %s", (id,))
    conn.commit()

    

    cursor.execute("SELECT * FROM gallery_events_gu WHERE id = %s", (id,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    cursor.execute("DELETE FROM gallery_events_gu WHERE id = %s", (id,))
    conn.commit()

    conn.close()

    return {"message": f"Member {id} deleted successfully"}


@app.get("/gallery_events_gu", response_model=List[Dict])
def get_all_gallery_events_gu():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM gallery_events_gu;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Fix images column if it's a JSON string
            if "images" in row_dict and row_dict["images"]:
                try:
                    row_dict["images"] = normalize_images(row_dict.get("images"))
                except Exception:
                    row_dict["images"] = []
            
            members.append(row_dict)
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/members_details_gu", response_model=List[Dict])
def get_all_members_details_gu():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM members_details_gu;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/members_details_en", response_model=List[Dict])
def get_all_members_details_en():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM members_details_en;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.get("/latest_members_details_en", response_model=List[Dict])
def get_all_members_details_en():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get all records from members_details
        query = "SELECT * FROM members_details_en ORDER BY id DESC LIMIT 10;"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to list of dictionaries
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]
        
        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/search_members_en")
def search_members_en(payload: dict):
    name = payload.get("name", "")

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM members_details_en
            WHERE fullname LIKE %s
            ORDER BY id DESC;
        """

        cursor.execute(query, (f"%{name}%",))
        results = cursor.fetchall()

        return results
    
    except mysql.connector.Error as e:
        return {"error": str(e)}
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.post("/add_member_en")
def add_member(member: MemberDetail):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO members_details_en ( fullname, address, birthdate)
        VALUES ( %s, %s, %s);
        """

        values = (
            member.fullname,
            member.address,
            member.birthdate
        )

        cursor.execute(query, values)
        connection.commit()

        new_id = cursor.lastrowid

        # Build full member object with srno
        new_member = {
            "srno": new_id,
            "fullname": member.fullname,
            "address": member.address,
            "birthdate": member.birthdate
        }

        new_member_gu = {
            "srno": new_id,
            "fullname": GoogleTranslator(source='auto', target='gu').translate(member.fullname),
            "address": GoogleTranslator(source='auto', target='gu').translate(member.address),
            "birthdate": member.birthdate
        }
        query_gu = """
        INSERT INTO members_details_gu (id, fullname, address, birthdate)
        VALUES (%s, %s, %s, %s);
        """

        values_gu = (
            new_member_gu["srno"],
            new_member_gu['fullname'],
            new_member_gu['address'],
            new_member_gu['birthdate']
        )
        cursor.execute(query_gu, values_gu)
        connection.commit()

        return {"message": "Member added successfully", "member": new_member}

    except mysql.connector.Error as e:
        print("MySQL Error:", e)   # 👈 this will show in your terminal
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.put("/update_member_en")
def update_member(member: UpdateMember):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    srno= member.id
    # 1. Check if member exists
    cursor.execute("SELECT * FROM members_details_en WHERE id = %s", (srno,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    # 2. Update member
    cursor.execute(
        """
        UPDATE members_details_en
        SET fullname = %s, address = %s, birthdate = %s
        WHERE id = %s
        """,
        (member.fullname, member.address, member.birthdate, srno),
    )
    conn.commit()

     # 1. Check if member exists
    cursor.execute("SELECT * FROM members_details_gu WHERE id = %s", (srno,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")
    
    cursor.execute(
        """
        UPDATE members_details_gu
        SET fullname = %s, address = %s, birthdate = %s
        WHERE id = %s
        """,
        (GoogleTranslator(source='auto', target='gu').translate(member.fullname),GoogleTranslator(source='auto', target='gu').translate(member.address), member.birthdate, srno),
    )
    conn.commit()
    conn.close()

    return {"message": f"Member {srno} updated successfully"}

@app.delete("/delete_member_en")
def delete_member(request: DeleteRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    srno= request.srno

    cursor.execute("SELECT * FROM members_details_en WHERE srno = %s", (srno,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    cursor.execute("DELETE FROM members_details_en WHERE srno = %s", (srno,))
    conn.commit()

    cursor.execute("SELECT * FROM members_details_gu WHERE srno = %s", (srno,))
    member = cursor.fetchone()

    if member is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Member not found")

    cursor.execute("DELETE FROM members_details_gu WHERE srno = %s", (srno,))
    conn.commit()

    conn.close()

    return {"message": f"Member {srno} deleted successfully"}

# Existing GET route
@app.get("/users", response_model=List[Dict])
def get_all_members_details_en():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM users;"
        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        members = [dict(zip(columns, row)) for row in rows]

        return members

    except mysql.connector.Error as e:
        return {"error": str(e)}

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/users")
def add_member(member: user):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO users ( first_name, last_name, phone, city, state)
        VALUES ( %s, %s, %s, %s, %s);
        """

        values = (
            member.first_name,
            member.last_name,
            member.phone,
            member.city,
            member.state,
        )

        cursor.execute(query, values)
        connection.commit()

        return {"message": "Member added successfully", "member": member.dict()}

    except mysql.connector.Error as e:
        print("MySQL Error:", e)   # 👈 this will show in your terminal
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/login")
def login(phone: str = Body(..., embed=True)):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE phone = %s;"
        cursor.execute(query, (phone,))
        user = cursor.fetchone()
        if user and user['status']=='approved':
            return {"success": True, "user": user}
        elif user and user['status']=='pending':
            return {"success": False, "message": "Your account is still pending approval."}
        else:
            return {"success": False, "message": "Invalid phone number"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )



@app.get("/users/pending")
def get_pending_users():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE status = 'pending';"
        cursor.execute(query)
        users = cursor.fetchall()

        return {"pending_users": users}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/users/approved")
def get_pending_users():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE status = 'approved' AND user_type = 'client';"
        cursor.execute(query)
        users = cursor.fetchall()

        return {"pending_users": users}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.put("/users/update_status")
def accept_users(request: UserUpdateRequest):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        phone = [request.phone]
        status = [request.status]
        # Update only users whose IDs are in the given list
        if status[0] == 'approved':
            query = "UPDATE users SET status = 'approved' WHERE phone IN (%s)"
        elif status[0] == 'denied':
            query = "UPDATE users SET status = 'denied' WHERE phone IN (%s)"
        elif status[0] == 'pending':
            query = "UPDATE users SET status = 'pending' WHERE phone IN (%s)"

        cursor.execute(query, tuple(phone))
        connection.commit()

        return {"message": "Users updated successfully"}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

