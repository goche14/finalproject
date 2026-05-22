from rest_framework import serializers
from .models import Category, Tag, Event, Registration, Review, EventMedia


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]




class EventListSerializer(serializers.ModelSerializer):
    """სიისთვის — მსუბუქი, ნაკლები ველი"""
    organizer_username = serializers.CharField(
        source="organizer.username",
        read_only=True
    )
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )
    registration_count = serializers.IntegerField(read_only=True)  # annotate-ისგან

    class Meta:
        model = Event
        fields = [
            "id", "title", "status", "event_type",
            "start_date", "end_date", "location",
            "max_attendees", "organizer_username",
            "category_name", "registration_count"
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    """ერთი event-ის სრული ინფო"""
    organizer = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source="tags",
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Event
        fields = [
            "id", "title", "description",
            "organizer", "category", "category_id",
            "tags", "tag_ids", "status", "event_type",
            "start_date", "end_date", "location",
            "max_attendees", "created_at"
        ]
        read_only_fields = ["organizer", "created_at"]

    def validate(self, attrs):
        
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and start >= end:
            raise serializers.ValidationError(
                {"end_date": "დასასრულის თარიღი უნდა იყოს დასაწყისზე გვიან."}
            )
        return attrs




class RegistrationSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "user_username", "status", "registered_at"]
        read_only_fields = ["user_username", "registered_at"]

    def validate(self, attrs):
        request = self.context["request"]
        event = self.context["event"]  

        
        if Registration.objects.filter(user=request.user, event=event).exists():
            raise serializers.ValidationError("უკვე დარეგისტრირებული ხართ.")

        
        confirmed_count = event.registrations.filter(status="confirmed").count()
        if confirmed_count >= event.max_attendees:
            raise serializers.ValidationError("ადგილები ამოიწურა.")

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        event = self.context["event"]
        return Registration.objects.create(
            user=request.user,
            event=event,
            **validated_data
        )




class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user_username", "rating", "comment", "created_at"]
        read_only_fields = ["user_username", "created_at"]

    def validate_rating(self, value):
        
        if not (1 <= value <= 5):
            raise serializers.ValidationError("რეიტინგი 1-5 შორის უნდა იყოს.")
        return value



class EventMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMedia
        fields = ["id", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]