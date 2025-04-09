// components/CustomTabBar.tsx
import { View, TouchableOpacity, StyleSheet, Text } from 'react-native';
import { useRouter, usePathname } from 'expo-router';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function CustomTabBar() {
    const router = useRouter();
    const pathname = usePathname();

    return (
    <View style={styles.tabBar}>
        <TouchableOpacity onPress={() => router.push("/")}>
            <View style={styles.tab}>
                <FontAwesome name="home" size={27} color={pathname === '/home' ? 'blue' : 'gray'} />
                <Text style={styles.tabText}>Home</Text>
            </View>
        </TouchableOpacity>
        
        <TouchableOpacity onPress={() => router.push('/camera')}>
            <View style={styles.tab}>

                <FontAwesome name="camera" size={27} color={pathname === '/camera' ? 'blue' : 'gray'} />
                <Text style={styles.tabText}>Camera</Text>
            </View>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => router.push('/settings')}>
            <View style={styles.tab}>
                <FontAwesome name="cog" size={27} color={pathname === '/setting' ? 'blue' : 'gray'} />
                <Text style={styles.tabText}>Settings</Text>
            </View>
        </TouchableOpacity>

    </View>
    );
}

const styles = StyleSheet.create({
    tabBar : {
        position: 'absolute',
        bottom: 0,
        flexDirection: 'row',
        justifyContent: 'space-around',
        width: '100%',
        backgroundColor: 'white',
        paddingVertical: 10,
        borderTopWidth: 2,
        borderTopColor: '#eee',
    },
    tab : {
        flexDirection : 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingHorizontal: 10,
        gap: 5, // Space between icon and text
    },
    tabText : {
        color : '#808080',
        fontSize : 13,
        fontWeight: 500
    }
});