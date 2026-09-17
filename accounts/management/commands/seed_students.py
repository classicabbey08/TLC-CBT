from django.core.management.base import BaseCommand
from accounts.models import User


STUDENTS = [
    # JSS1
    ("Taiwo", "Anuoluwapo", "JSS1", "TLC/JSS1/001", "001"),
    ("Anosike", "Neymar", "JSS1", "TLC/JSS1/002", "002"),
    ("Bello", "Sofiat", "JSS1", "TLC/JSS1/003", "003"),
    ("Muritala", "Islamiyah", "JSS1", "TLC/JSS1/004", "004"),
    ("Olonimoyo", "Olamilekan", "JSS1", "TLC/JSS1/005", "005"),
    ("Oluwaferanmi", "Abubakar", "JSS1", "TLC/JSS1/006", "033"),

    # JSS2
    ("Adelani", "Ajoke", "JSS2", "TLC/JSS2/001", "006"),
    ("Agada", "Esther", "JSS2", "TLC/JSS2/002", "007"),
    ("Ifesanya", "Praise", "JSS2", "TLC/JSS2/003", "008"),
    ("Umar", "Seyi", "JSS2", "TLC/JSS2/004", "009"),
    ("Oluwadamilare", "Desire", "JSS2", "TLC/JSS2/005", "010"),
    ("Salami", "Maleek", "JSS2", "TLC/JSS2/006", "011"),
    ("Olakunle", "Ayomide", "JSS2", "TLC/JSS2/007", "030"),

    # JSS3
    ("Amehin", "Success", "JSS3", "TLC/JSS3/001", "012"),
    ("Oyenuga", "Anuoluwapo", "JSS3", "TLC/JSS3/002", "013"),
    ("Okegbemi", "Fadilullah", "JSS3", "TLC/JSS3/003", "014"),
    ("Adisa", "Amirat", "JSS3", "TLC/JSS3/004", "015"),
    ("Bello", "Sahadat", "JSS3", "TLC/JSS3/005", "016"),

    # SSS1
    ("Olusegun", "Eniola", "SSS1", "TLC/SSS1/001", "017"),
    ("Oni", "Mustapha", "SSS1", "TLC/SSS1/002", "018"),
    ("Adisa", "Aliat", "SSS1", "TLC/SSS1/003", "019"),
    ("Agada", "Gloria", "SSS1", "TLC/SSS1/004", "020"),
    ("Wilson", "David", "SSS1", "TLC/SSS1/005", "021"),

    # SSS2
    ("Mulero", "Sesi", "SSS2", "TLC/SSS2/001", "022"),
    ("Taiwo", "Tobiloba", "SSS2", "TLC/SSS2/002", "023"),
    ("Oyenuga", "Emmanuel", "SSS2", "TLC/SSS2/003", "024"),
    ("Ikeh", "Joshua", "SSS2", "TLC/SSS2/004", "031"),

    # SSS3
    ("Jaiyeola", "Lateefah", "SSS3", "TLC/SSS3/001", "025"),
    ("Okegbemi", "Faridat", "SSS3", "TLC/SSS3/002", "026"),
    ("Orija", "Opeyemi", "SSS3", "TLC/SSS3/003", "027"),
    ("Olajide", "Oluwakemisola", "SSS3", "TLC/SSS3/004", "028"),
    ("Hassan", "Oluwaseun", "SSS3", "TLC/SSS3/005", "029"),
    ("Ikeh", "John", "SSS3", "TLC/SSS3/006", "032"),
]


class Command(BaseCommand):
    help = "Seed all TLC students with their assigned 3-digit PINs"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for first, last, klass, adm, pin in STUDENTS:
            username = adm.replace("/", "_").lower()

            user, created = User.objects.get_or_create(
                admission_number=adm,
                defaults={
                    "username": username,
                    "first_name": first,
                    "last_name": last,
                    "role": User.Role.STUDENT,
                    "student_class": klass,
                },
            )

            user.username = username
            user.first_name = first
            user.last_name = last
            user.role = User.Role.STUDENT
            user.student_class = klass

            # Assign the student's unique PIN
            user.set_password(pin)
            user.save()

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {adm} – {first} {last} | PIN: {pin}"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated: {adm} – {first} {last} | PIN: {pin}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created_count}, Updated: {updated_count}"
            )
        )

