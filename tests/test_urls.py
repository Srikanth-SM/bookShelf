from django.urls import reverse, resolve

print("sample")


class Test_urls:
    def test_home(self):
        path = reverse("home")
        assert (resolve(path).url_name == "home")

    def test_get_all_books(self):
        path = reverse("get_all_books")
        assert (resolve(path).url_name == "get_all_books")

    def test_book_a_book(self):
        path = reverse("book_a_book", kwargs={
            "book_id": 1,
            "book_instance_id": str(1)
        })
        assert (resolve(path).url_name == "book_a_book")

    def test_update_book(self):
        path = reverse("update_book", kwargs={"pk": 1})
        assert (resolve(path).view_name == "update_book")

    def test_book_detail(self):
        path = reverse("book_detail", kwargs={"pk": 0})
        assert(resolve(path).view_name == "book_detail")

    def test_add_book(self):
        path = reverse("add_book")
        assert(resolve(path).view_name == "add_book")

    def test_delete_book(self):
        path = reverse("delete_book", kwargs={
            "pk": 1})
        assert(resolve(path).view_name == "delete_book")

    def test_delete_book_instance(self):
        path = reverse("delete_book_instance", kwargs={
            "book_id": 1,
            "book_instance_id": 1
        })
        assert(resolve(path).view_name == "delete_book_instance")

    def test_update_book_instance(self):
        path = reverse("update_book_instance", kwargs={
            "book_id": 1,
            "book_instance_id": 1
        })
        assert (resolve(path).view_name == "update_book_instance")

    def test_return_book(self):
        path = reverse("return_book", kwargs={
            "book_id": 1,
            "book_instance_id": 1
        })
        assert (resolve(path).view_name == "return_book")

    def test_add_book_instance(self):
        path = reverse("add_book_instance")
        assert(resolve(path).view_name == "add_book_instance")
