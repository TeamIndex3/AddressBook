from peewee import *
from fileUtils import *
from contact import ContactDAO

# Instantiate SqliteDatabase object that models will use to persist data.
DATABASE = 'application.db'
db = SqliteDatabase(DATABASE) # db manages the connection and executes queries


class BaseModel(Model):
    """ Standard base model class that specifies which database to use.
    Subclasses automatically use correct storage """
    class Meta:
        database = db


class AddressBook(BaseModel):
    """ The AddressBook object model representing a single collection
    of contacts
    :param name: A string, the name of the book given by user.
    :param id: An int, the auto-incrementing integer primary key field.
    """
    name = CharField(unique=True)

    class Meta:
        order_by = ('id',)


class Contact(BaseModel):
    """ A representation of an addressbook contact in the database. By
    default, Contacts are ordered by last name.
    :param ab: An int, the foreign key used to map a Contact to the
    AddressBook it belongs to.
    """
    first_name = CharField()
    last_name = CharField()
    address = CharField()
    city = CharField()
    state = CharField()
    zip_code = CharField(null=False)
    phone = CharField()
    email = CharField()
    ab = ForeignKeyField(AddressBook)

    class Meta:
        order_by = ('last_name',)


def create_tables():
    """ Creates the tables in the database containing the AddressBook
    and Contact models. Only needs to be performed once at the initialization
    of the app. """
    db.connect()
    db.drop_tables([AddressBook, Contact])
    db.create_tables([AddressBook, Contact],True)

# first_name =
# last_name =
# address =
# city =
# state =
# zip_code =
# phone =
# email =


def create_addressbook(name):
    """ Creates a new AddressBook record. If an AddressBook already exists
    with the name provided, the database will raise an IntegrityError.
    :param name: string, the name of the Addressbook
    """
    try:
        with db.transaction():
            addressbook = AddressBook.create(
                name=name,
            )
        return addressbook
    except IntegrityError:
        print 'Addressbook already exists'


def create_contact(contact, ab):
    """ Creates a new Contact and prints out the number of rows modified.
    :param contact: object, the ContactDAO to be created.
    :param ab: int, the id of the AddressBook the Contact will be added to.
    """
    try:
        with db.transaction():
            person = Contact.create(
                first_name=contact.first_name,
                last_name=contact.last_name,
                address=contact.address,
                city=contact.city,
                state=contact.state,
                zip_code=contact.zip_code,
                phone=contact.phone,
                email=contact.email,
                ab=ab
            )
        # print person.save() # Prints 1 if successful
        print_info(person)
        return person.id # Return id of Contact
    except IntegrityError:
        print 'Contact already exists'

def search_contacts(last, first, ab):
    """ Returns a list of Contacts in an AddressBook matching search input.
    :param last: string, last name of Contact to search for.
    :param first: string, first name of Contact to search for.
    :param ab: int, id of AddressBook being searched.
    """
    results = []
    query = Contact.select().where(
        (Contact.last_name == last) &
        (Contact.first_name == first) &
        (Contact.ab == ab))
    for contact in query:
        print "Found: "
        print_info(contact)
        results.append(contact)
    return results


def string_search(info, ab):
    results = Contact.select().where(
        (Contact.ab == ab) & (
            (Contact.first_name.contains(info)) |
            (Contact.last_name.contains(info)) |
            (Contact.address.contains(info)) |
            (Contact.city.contains(info)) |
            (Contact.state.contains(info)) |
            (Contact.zip_code.contains(info)) |
            (Contact.phone.contains(info)) |
            (Contact.email.comtains(info))
        ))
    for result in results:
        print_info(result)


def delete_contact(contact):
    contact.delete_instance()


def print_info(contact):
    print contact.first_name + " " + contact.last_name + " " + contact.address + " " + contact.city + " " + contact.state + " " + contact.zip_code + " " + contact.phone + " " + contact.email


def populate_addressbook(id,csv_file=None):
    """ Adds Contacts from a csv file to an AddressBook. Calls method
    import_csv from fileUtils.py to read csv into dictionary.
    :param id: int, the id of the AddressBook to add Contacts to.
    :param csv_file: string, the file name of the csv to import.
    """
    contact_data = import_csv(csv_file, id)
    with db.atomic():
        for data_dict in contact_data:
            Contact.create(**data_dict)
    print "Created contacts in book with id " + str(id)

if __name__ == "__main__":
    BOOK = 'Book01'
    DATA_FILE = 'dataOct-13-2015.csv'

    create_tables()
    addressbook = create_addressbook(BOOK)

    # Fill addressbook with data in DATA_FILE
    print "Populating addressbook..."
    populate_addressbook(addressbook.id, DATA_FILE)

    num_contacts = Contact.select().count()
    print addressbook.name+" now has "+str(num_contacts)+" contacts!"

    person1 = ContactDAO(['Smith','Hannah','992 E 18th','eugene','oregon','97403','5039367858','hus@uoregon.edu'])
    print "Inserting "+person1.first_name+" "+person1.last_name+" into "+addressbook.name
    person1_id = create_contact(person1, addressbook.id)

    person2 = ContactDAO(['Doe','Van','2954 NE 30th','Portland','OR','97212','5032818856','vps@juno.com'])
    create_contact(person2, addressbook.id)
    print "Retrieving contact named "+person2.first_name+" from "+addressbook.name
    get_person2 = Contact.get(Contact.first_name == person2.first_name)
    print_info(get_person2)

    print "Deleting "+person1.first_name+" from "+addressbook.name
    del_person1 = Contact.get(Contact.id == person1_id)
    del_person1.delete_instance()

    try:
        Contact.get(Contact.id == person1_id)
    except DoesNotExist:
        print "Deletion successful!"
